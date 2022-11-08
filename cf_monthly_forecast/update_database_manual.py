import cdsapi
import os 
from cf_monthly_forecast.config import *
from cf_monthly_forecast.utils import reduce_vars, derive_path
from cf_monthly_forecast.download_monthly_operational import split_grib, convert_grib_to_netcdf
import cf_monthly_forecast.monthly_fc_input as mfin
import cf_monthly_forecast.subdaily_fc_input as sdfin

def main(center,system,months,variables=None,mode='monthly',years=None):

    if mode == 'monthly':
        input_dict = mfin.input_dict.copy()

    input_dict['originating_centre'] = center
    input_dict['system'] = system
    if variables is None:
        # use 'standard' set of variables as defined in *_fc_input.py
        input_dict['variable'] = reduce_vars(center,mode=mode)
    else:
        input_dict['variable'] = variables

    if mode == 'monthly':
        if years is None:
            input_dict['year'] = [str(my).zfill(4) for my in range(mfin.hc_range[0],mfin.hc_range[-1]+1)]
        else:
            input_dict['year'] = years
    
        c = cdsapi.Client()
        lookup_path = derive_path(center,mode='monthly')
        temp_dir = os.path.join(proj_base,'data/tmp/')

        for MO in months:
            input_dict['month'] = str(MO).zfill(2)

            outfile = '{prd:s}_{mod:s}_{sys:s}_{hcs:0<4d}-{hce:0<4d}_{mon:0>2d}.grib'.format(
                        mon = MO,
                        mod = center,
                        prd = mfin.PRODUCT,
                        hcs = mfin.hc_range[0],
                        hce = mfin.hc_range[-1],
                        sys = system
                    )

            outfile_abs = os.path.join(temp_dir,outfile)

            # print('seasonal-{0:s}-single-levels'.format(mfin.temp_res),input_dict,outfile_abs)

            c.retrieve(
                'seasonal-{0:s}-single-levels'.format(mfin.temp_res),
                input_dict,
                outfile_abs
            )

            grib_split_hc,splt_date_key = split_grib(outfile_abs,mode='hindcast',product_type='monthly',delete_input=True)
            
            convert_grib_to_netcdf(
                grib_split_hc,
                lookup_path,
                mode        = 'hindcast',
                split_keys  = ['[shortName]',splt_date_key],
                prod_type   ='monthly'
            )

    else:
        print('subdaily manual hindcast update not implemented yet!')

if __name__ == '__main__':
    
    # INPUT (which center, new system number, which months)
    center = 'ecmwf' # must be string
    system = '51' # must be string
    months = list(range(11,13)) # must be list
    variables = None # must be list
    years = None # must be list
    mode = 'monthly' # must be string

    main(center,system,months,variables=variables,mode=mode,years=years)