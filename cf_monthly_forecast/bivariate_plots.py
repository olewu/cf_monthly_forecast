import xarray as xr
import os
import subprocess as sbp
from datetime import datetime
from dateutil.relativedelta import relativedelta
from calendar import monthrange
import sys

from cf_monthly_forecast.config import *
from cf_monthly_forecast.utils import quadrant_probs,find_closest_gp
from cf_monthly_forecast.plots import bivariate_fc_plot,derive_abs_limits
from cf_monthly_forecast.utils import send_email

def bivariate_fc_sequence(x_var,y_var,INIT_MON,INIT_YEA,MODE,ref_clim,locations=city_coords_lalo):

    x_ds = xr.open_dataset(dirs['SFE_forecast'] + '/forecast_production_detailed_{2:s}_{1:d}_{0:d}.nc4'.format(INIT_MON,INIT_YEA,x_var))
    y_ds = xr.open_dataset(dirs['SFE_forecast'] + '/forecast_production_detailed_{2:s}_{1:d}_{0:d}.nc4'.format(INIT_MON,INIT_YEA,y_var))
    
    ds_val = xr.open_dataset('/projects/NS9853K/DATA/SFE/Validation_Dataset/sfe_benchmark.nc4')

    init_date = datetime(INIT_YEA,INIT_MON,1)

    # find closest grid points to the required ones:
    closest_gp_dict = find_closest_gp(locations,mode=MODE)

    for (loc_name,latlon) in closest_gp_dict.items():
        # find closest grid point:
        x_loc = x_ds.sel(lat=latlon[0],lon=latlon[1])
        y_loc = y_ds.sel(lat=latlon[0],lon=latlon[1])

        x_clim_loc = ds_val['{0:s}_{1:s}'.format(x_var,ref_clim)].sel(forecast_month=INIT_MON,lat=latlon[0],lon=latlon[1])
        y_clim_loc = ds_val['{0:s}_{1:s}'.format(y_var,ref_clim)].sel(forecast_month=INIT_MON,lat=latlon[0],lon=latlon[1])
        
        for LEA_M in [1,2,3]: # LEA_M is the coordinate value for lead_month, not the index! climatology only exists for first 3 lead months!
            print(LEA_M,loc_name,latlon)

            # extract relevant lead month:
            x_loc_lea = x_loc.sel(lead_month=LEA_M)
            y_loc_lea = y_loc.sel(lead_month=LEA_M)

            x_clim_loc_lea = x_clim_loc.sel(lead_month=LEA_M)
            y_clim_loc_lea = y_clim_loc.sel(lead_month=LEA_M)


            # derive quadrant probabilities for forecast ensemble:
            probs4 = quadrant_probs(
                x_loc_lea.forecast,
                y_loc_lea.forecast,
                x_loc_lea.climatology,
                y_loc_lea.climatology
            )

            # climatological quadrant probabilities 
            clim_probs4 = quadrant_probs(
                x_clim_loc_lea,
                y_clim_loc_lea
            )
            
            plt_lims = derive_abs_limits(x_loc_lea,y_loc_lea)

            fc_date = init_date + relativedelta(months=LEA_M)
            TITLE = '{:s}, {:s} {:d}'.format(loc_name,fc_date.strftime('%B'),fc_date.year)
            savepath = '{0:s}/monthly_fc/init_{1:s}-{2:s}/bivariate_loc/'.format(
                dirs['public'],str(INIT_YEA).zfill(4),str(INIT_MON).zfill(2)
            )
            if not os.path.exists(savepath):
                os.makedirs(savepath)
            figname = '{x:s}-vs-{y:s}_{c:s}_{m:0>2d}'.format(
                x = x_var,
                y = y_var,
                c = loc_name.replace('å','aa').replace('ø','o').replace('æ','ae'),
                m = fc_date.month
            )

            fc_mon_len = monthrange(fc_date.year,fc_date.month)
            if x_var == 'total_precipitation':
                x_fac = 1000*fc_mon_len[1]
            else:
                x_fac = None
            if y_var == 'total_precipitation':
                y_fac = 1000*fc_mon_len[1]
            else:
                y_fac = None

            # make scatter plot of the forecast data
            bivariate_fc_plot(
                x_loc_lea.forecast,
                y_loc_lea.forecast,
                x_loc_lea.climatology,
                y_loc_lea.climatology,
                fc_probs = probs4,
                clim_probs = clim_probs4,
                plt_lims = plt_lims,
                x_var_name = x_var,
                y_var_name = y_var,
                x_fac = x_fac,
                y_fac = y_fac,
                title = TITLE,
                save_path = savepath,
                fig_name = figname
            )

if __name__ == '__main__':

    x_var = '2m_temperature'
    y_var = 'total_precipitation'

    # direct print output to log file:
    logfile_path = '{0:s}/logs/fc_bivariate_plt.log'.format(proj_base)
    sys.stdout = open(logfile_path, 'a')

    tday = datetime.today()
    inityear,initmonth = tday.year,tday.month
    
    filename_x = '{0:s}/forecast_production_detailed_{3:s}_{1:d}_{2:d}.nc4'.format(dirs['SFE_forecast'],inityear,initmonth,x_var)
    filename_y = '{0:s}/forecast_production_detailed_{3:s}_{1:d}_{2:d}.nc4'.format(dirs['SFE_forecast'],inityear,initmonth,y_var)

    if os.path.isfile(filename_x) and os.path.isfile(filename_y):
        print('{0:} (UTC)\tForecast files exist, creating plots:\n'.format(datetime.now()))
    else:
        print('{0:} (UTC)\tForecast files {1:s} and/or {2:s} do not exist!\n'.format(datetime.now(),filename_x,filename_y))
        sys.exit()

    try:
        bivariate_fc_sequence(
            x_var,
            y_var,
            initmonth,
            inityear,
            'land',
            'obs',
            locations=city_coords_lalo
        )

        # write an index file if the script executes as expected:
        idx_file = '{0:s}/data/index/complete_biv_{1:d}-{2:s}.ix'.format(proj_base,inityear,str(initmonth).zfill(2))

        # only write the file if it doesn't exist already (inidicating previous successful execution)
        # no automatic clean-up of the directory is done (writing a file every month), so occasinally clean up manually.
        if not os.path.isfile(idx_file):
            sbp.call(
                'touch {0:s}'.format(idx_file),
                shell=True
            )

            subj = 'Successful: Bivariate plot plot production done {:}'.format(datetime.now())
            send_email(subj,subj)
    except Exception as e:
        print(e)
        subj = 'Failed: Bivariate plot production failed {:}'.format(datetime.now())
        text = 'Bivariate plot production failed with error: {1:}\nCheck {0:s} for detailed error message.'.format(logfile_path,e)
        send_email(subj,text)