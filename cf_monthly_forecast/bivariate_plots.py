import xarray as xr
import os
import subprocess as sbp
from datetime import datetime
from dateutil.relativedelta import relativedelta
from calendar import monthrange
import sys
import json

from cf_monthly_forecast.config import *
from cf_monthly_forecast.utils import quadrant_probs,find_closest_gp, get_station_stats, predict_from_monthly_trend, get_station_data, send_email
from cf_monthly_forecast.plots import bivariate_fc_plot,derive_abs_limits

# INIT_MON = initmonth
# INIT_YEA = inityear
# MODE = 'land'
# ref_clim = 'stat'
# locations=city_coords_lalo.copy()
def bivariate_fc_sequence(x_var,y_var,INIT_MON,INIT_YEA,MODE,ref_clim,locations=city_coords_lalo):
    """
    Note that ref_clim = 'obs'  takes ERA5 as climatology, choose ref_clim = 'stat' for actual observed station normals!
    """

    if ref_clim == 'stat':
        # need to rescale the fc output in this case!
        if not (x_var in ['2m_temperature','total_precipitation'] and y_var in ['2m_temperature','total_precipitation']):
            print('can only get station normals for temperature and precip currently')
            sys.exit()
        clim_mean_mode = 'stat'
        # drop Trondheim from the list due to the current lack of sufficient data
        locations.pop('Trondheim')
    else:
        clim_mean_mode = None
    x_ds = xr.open_dataset(dirs['SFE_monthly'] + '/{2:s}/forecast_production_detailed_{2:s}_{1:d}_{0:0>2d}.nc'.format(INIT_MON,INIT_YEA,x_var))
    y_ds = xr.open_dataset(dirs['SFE_monthly'] + '/{2:s}/forecast_production_detailed_{2:s}_{1:d}_{0:0>2d}.nc'.format(INIT_MON,INIT_YEA,y_var))
    
    ds_val = xr.open_dataset(dirs['SFE_validation'] + '/sfe_benchmark.nc4')

    init_date = datetime(INIT_YEA,INIT_MON,1)

    # find closest grid points to the required ones:
    closest_gp_dict = find_closest_gp(locations,mode=MODE)
    # closest_gp_dict_ = find_closest_gp(locations,mode=MODE,vers='old')

    for (loc_name,latlon) in closest_gp_dict.items():
        # find closest grid point:
        x_loc = x_ds.sel(lat=latlon[0],lon=latlon[1])
        y_loc = y_ds.sel(lat=latlon[0],lon=latlon[1])

        if ref_clim != 'stat':
            # climatology (ERA5 & forecast system)
            # x_clim_loc = ds_val['{0:s}_{1:s}'.format(x_var,ref_clim)].sel(forecast_month=INIT_MON,lat=latlon[0],lon=latlon[1])
            # y_clim_loc = ds_val['{0:s}_{1:s}'.format(y_var,ref_clim)].sel(forecast_month=INIT_MON,lat=latlon[0],lon=latlon[1])
            x_clim_loc = ds_val['{0:s}_{1:s}'.format(x_var,ref_clim)].sel(forecast_month=INIT_MON,lat=closest_gp_dict[loc_name][0],lon=closest_gp_dict[loc_name][1])
            y_clim_loc = ds_val['{0:s}_{1:s}'.format(y_var,ref_clim)].sel(forecast_month=INIT_MON,lat=closest_gp_dict[loc_name][0],lon=closest_gp_dict[loc_name][1])
        else:
            # x_clim_loc = ds_val['{0:s}_nwp'.format(x_var)].sel(forecast_month=INIT_MON,lat=latlon[0],lon=latlon[1])
            # y_clim_loc = ds_val['{0:s}_nwp'.format(y_var)].sel(forecast_month=INIT_MON,lat=latlon[0],lon=latlon[1])
            # x_clim_loc = ds_val['{0:s}_nwp'.format(x_var)].sel(forecast_month=INIT_MON,lat=closest_gp_dict[loc_name][0],lon=closest_gp_dict[loc_name][1])
            # y_clim_loc = ds_val['{0:s}_nwp'.format(y_var)].sel(forecast_month=INIT_MON,lat=closest_gp_dict[loc_name][0],lon=closest_gp_dict[loc_name][1])
            x_clim_loc = ds_val['{0:s}_nwp'.format(x_var)].sel(forecast_month=INIT_MON).interp(lat=closest_gp_dict[loc_name][0],lon=closest_gp_dict[loc_name][1])
            y_clim_loc = ds_val['{0:s}_nwp'.format(y_var)].sel(forecast_month=INIT_MON).interp(lat=closest_gp_dict[loc_name][0],lon=closest_gp_dict[loc_name][1])
        
            # get stations stats and trend prediction ahead of looping:
            stat_id = station_ids[loc_name]
            stat_data = get_station_data(stat_id)
            mean_stat,std_stat = get_station_stats(stat_id)
            stat_trend = predict_from_monthly_trend(stat_id,pred_years=[INIT_YEA,INIT_YEA+1])

        for LEA_M in [1,2,3]: # LEA_M is the coordinate value for lead_month, not the index! climatology only exists for first 3 lead months!
            print(LEA_M,loc_name,latlon)
            
            # derive forecast date:
            fc_date = init_date + relativedelta(months=LEA_M)
            
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

            if ref_clim == 'stat':
                FC_MON = fc_date.month
                clim_probs4_stat = quadrant_probs(
                    stat_data.where(stat_data.time.dt.month==FC_MON).dropna('time')[x_var],
                    stat_data.where(stat_data.time.dt.month==FC_MON).dropna('time')[y_var],
                    mean_stat.sel(month=FC_MON)[x_var],
                    mean_stat.sel(month=FC_MON)[y_var],
                )

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
            elif x_var == '2m_temperature':
                x_fac = 1
            else:
                x_fac = None
            if y_var == 'total_precipitation':
                y_fac = 1000*fc_mon_len[1]
            elif y_var == '2m_temperature':
                y_fac = 1
            else:
                y_fac = None

            if clim_mean_mode is None:
                clim_x_pass = x_loc_lea.climatology
                clim_y_pass = y_loc_lea.climatology
                fc_x_pass = x_loc_lea.forecast
                fc_y_pass = y_loc_lea.forecast

                plt_lims = derive_abs_limits(fc_x_pass,fc_y_pass,x_center=clim_x_pass,y_center=clim_y_pass,x_sd=x_loc_lea.sd,y_sd=y_loc_lea.sd)

                clim_sel_x, clim_sel_y = None, None
                x_pred_trend, y_pred_trend = None, None

            else:
                clim_x_pass = mean_stat.sel(month=FC_MON)[x_var]
                clim_y_pass = mean_stat.sel(month=FC_MON)[y_var]

                x_sd = std_stat.sel(month=FC_MON)[x_var]
                y_sd = std_stat.sel(month=FC_MON)[y_var]

                y_fac = 1
                x_fac = 1
                # standardize:
                fc_x_pass = ((x_loc_lea.forecast - x_loc_lea.climatology)/x_loc_lea.sd)*x_sd + clim_x_pass
                # if variable is precipitation, set all negative precip amounts to zero (happens frequently due bias correction)
                if x_var == 'total_precipitation':
                    fc_x_pass[fc_x_pass < 0] = 0
                fc_y_pass = ((y_loc_lea.forecast - y_loc_lea.climatology)/y_loc_lea.sd)*y_sd + clim_y_pass
                if y_var == 'total_precipitation':
                    fc_y_pass[fc_y_pass < 0] = 0

                x_pred_trend = stat_trend.sel(month=FC_MON,year=fc_date.year)[x_var]
                y_pred_trend = stat_trend.sel(month=FC_MON,year=fc_date.year)[y_var]

                clim_sel = stat_data.where(stat_data.time.dt.month==FC_MON).dropna('time')
                clim_sel_x, clim_sel_y = clim_sel[x_var], clim_sel[y_var]

                plt_lims = derive_abs_limits(fc_x_pass,fc_y_pass,x_center=clim_x_pass,y_center=clim_y_pass,x_sd=x_sd,y_sd=y_sd)

            # make scatter plot of the forecast data
            bivariate_fc_plot(
                fc_x_pass,
                fc_y_pass,
                clim_x_pass,
                clim_y_pass,
                clim_x = clim_sel_x,
                clim_y = clim_sel_y,
                fc_probs = probs4,
                clim_probs = clim_probs4,
                plt_lims = None,
                x_var_name = x_var,
                y_var_name = y_var,
                x_fac = x_fac,
                y_fac = y_fac,
                x_pred = x_pred_trend,
                y_pred = y_pred_trend,
                title = TITLE,
                save_path = savepath,
                fig_name = figname
            )

if __name__ == '__main__':

    x_var = '2m_temperature'
    y_var = 'total_precipitation'

    # direct `print` output to log file:
    logfile_path = '{0:s}/logs/fc_bivariate_plt.log'.format(proj_base)
    sys.stdout = open(logfile_path, 'a')

    tday = datetime.today()
    inityear,initmonth = tday.year,tday.month
    
    filename_x = '{0:s}/{3:s}/forecast_production_detailed_{3:s}_{1:d}_{2:0>2d}.nc'.format(dirs['SFE_monthly'],inityear,initmonth,x_var)
    filename_y = '{0:s}/{3:s}/forecast_production_detailed_{3:s}_{1:d}_{2:0>2d}.nc'.format(dirs['SFE_monthly'],inityear,initmonth,y_var)

    # derive set of models in MME from the system dimension of the above file(s):
    with xr.open_dataset(filename_x) as DS:
        participating_systems_id = set(DS.system.values)
    participating_systems = [dt_systems_lookups[int(ps)] for ps in participating_systems_id]
    # save to json for other pltting routines to look up systems:
    ps_filename = os.path.join('{0:s}'.format(dirs['processed']),'systems_{0:d}-{1:0>2d}.json'.format(inityear,initmonth))
    with open(ps_filename, 'w') as f:
        json.dump(participating_systems, f)

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
            'stat',
            locations=city_coords_lalo.copy()
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
