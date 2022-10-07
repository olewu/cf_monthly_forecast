import cdsapi
from glob import glob
import subprocess as sbp
import os 
import sys
from datetime import datetime
import re
import pandas as pd
from cf_monthly_forecast.config import *
from cf_monthly_forecast.utils import sysnum_from_grib, get_missing_hindcast_fields, reduce_vars, derive_path
import cf_monthly_forecast.monthly_fc_input as mfin

def main(init_date):
    # provide the desired month and year of initialization for the download:

    print('Downloading for start date {:}'.format(init_date))

    YEAR = str(init_date.year)
    MONTH = str(init_date.month).zfill(2)

    # print output to log file for each initialization:
    logfile_path = '{0:s}/logs/download_monthly_oper_{1:s}_{2:s}.log'.format(proj_base,YEAR,MONTH)
    sys.stdout = open(logfile_path, 'a')

    # directory to save temporary files to:
    temp_dir = os.path.join(proj_base,'data/tmp/')
    # create directory if it doesn't exist already
    os.makedirs(temp_dir,exist_ok=True)

    #----------------0) PREPARE INPUT FIELDS----------------#
    # get a copy of the input dictionary with the constant input:
    input_dict = mfin.input_dict.copy()

    # add date dependent (forecast year and month) fields:
    input_dict['year'] = YEAR
    input_dict['month'] = MONTH

    # start a cdsapi client:
    c = cdsapi.Client()

    for MODEL in all_models:
        # add current model to input dict:
        input_dict['originating_centre'] = MODEL
        input_dict['variable'] = reduce_vars(MODEL,mode='monthly')
        
        # name + location of output file:
        filename_fc = '{prd:s}_{mod:s}_latest_{ye:s}_{mon:s}.grib'.format(
            ye  = YEAR,
            mon = MONTH,
            mod = MODEL,
            prd = mfin.PRODUCT
        )
        outfile_fc = os.path.join(temp_dir,filename_fc)

        #----------------1.1) RETRIEVE LATEST FORECAST----------------#
        # note that the 'system' key is delibaretely left out of the request to obtain the latest system, 
        # whatever its system number is. It might have changed, but we don't have to specify it, so that doesn't matter here

        if not os.path.exists(outfile_fc):
            # note that this will currently execute as soon as `outfile_fc` does not exist, which also happens if the download was made and the file split!

            # send request for forecast:
            c.retrieve(
                'seasonal-{0:s}-single-levels'.format(mfin.temp_res),
                input_dict,
                outfile_fc
            )
        else:
            print('{0:s} already downloaded'.format(outfile_fc))
        
        
        #----------------2) INFER SYSTEM NUMBER----------------#
        # retrieve the model version number of the latest forecast to be able to get the corresponding hindcasts:
        # run grib_ls to look for the system keyword in the grib file and redirect output
        SYSTEM = sysnum_from_grib(outfile_fc)

        print('Latest {0:s} forecast for {2:s}-{3:s} has system number {1:s}'.format(MODEL,SYSTEM,YEAR,MONTH))
        #----WARNING----#
        # this is definitely not the smartest way of looking up the model number. 
        # The index of the split output (2) is hard coded and it should be that grib_ls outputs the file in the first line, 
        # keyword (here: system) in the second line and the gives the values for the keyword from there on. 
        # If the grib exists but returns no (0) messages, line 3 will be empty and the regex search will fail

        #----------------1.2) SPLIT BY VARIABLE & CONVERT TO NETCDF----------------#
        # split forecast:
        if os.path.exists(outfile_fc):
            print('splitting forecast grib file')
            grib_split_fc = split_grib(outfile_fc,mode='forecast',product_type='monthly',delete_input=True)
        
        lookup_path = derive_path(MODEL,mode='monthly')

        # do conversion of every single split file:
        convert_grib_to_netcdf(
            grib_split_fc,
            lookup_path,
            mode        = 'forecast',
            split_keys  = ['[shortName]'],
            prod_type   ='monthly',
            system_num  = SYSTEM
        )

        #----------------2.1) DOWNLOAD CORRESPONDING HINDCASTS 1993 - 2016 (IF NEEDED)----------------#
        # now that we know the system number, we can get the corresponding hindcasts (here, the system number matters!)
        # check if they already exist, which is possible since the systems don't get updated so frequently:
        
        # first copy the input directory from the forecasts and add the system number as well as hindcast years:
        input_dict_hc = input_dict.copy()
        # dump the forecast year:
        input_dict_hc.pop('year')
        # include system number derived above:
        input_dict_hc['system'] = SYSTEM
        
        # the check has to derive the neccesity of downloading from the split nc files (single variables) in the new structure!
        missing_vars, missing_years = get_missing_hindcast_fields(MODEL,SYSTEM,MONTH,mode='monthly')

        # Do retrieval of the missing years + variables (if any)        
        filename_hc = '{prd:s}_{mod:s}_{sys:s}_{hcs:0<4d}-{hce:0<4d}_{mon:s}.grib'.format(
            mon = MONTH,
            mod = MODEL,
            prd = mfin.PRODUCT,
            hcs = mfin.hc_range[0],
            hce = mfin.hc_range[-1],
            sys = SYSTEM
        )
        outfile_hc = os.path.join(temp_dir,filename_hc)
        
        if missing_vars:
            input_dict_hc['variable'] = missing_vars
            input_dict_hc['year'] = [str(my).zfill(4) for my in set(missing_years)]

            # Download:
            if not os.path.exists(outfile_hc):
                c.retrieve(
                    'seasonal-{0:s}-single-levels'.format(mfin.temp_res),
                    input_dict_hc,
                    outfile_hc
                )
        else:
            print('All requested hindcasts for {0:s} 1993-2016 already exist.'.format(MONTH))

        #----------------2.2) SPLIT BY VARIABLE & CONVERT TO NETCDF----------------#
        # split hindcasts in the same manner (must include hindcast year in split),  this can take up to 2 mins:
        grib_split_hc,splt_date_key = split_grib(outfile_hc,mode='hindcast',product_type='monthly',delete_input=True)
        
        convert_grib_to_netcdf(
            grib_split_hc,
            lookup_path,
            mode        = 'hindcast',
            split_keys  = ['[shortName]',splt_date_key],
            prod_type   ='monthly'
        )

def convert_grib_to_netcdf(split_files,target_path,mode,split_keys=['[shortName]'],prod_type='monthly',system_num=None):
    """

    """

    if prod_type == 'monthly':
        product = mfin.PRODUCT
        var_df = mfin.variables_df
    # elif prod_type == 'subdaily':
        # product = sdfin.PRODUCT
    #     var_df = sdfin.variables_df

    assert split_keys, 'need to pass a list with at least one keyword to `split_keys'

    split_wildcard = split_files
    for sk in split_keys:
        split_wildcard = split_wildcard.replace(sk,'*')

    split_names = glob(split_wildcard)
    # convert forecasts for single variables:
    for sngl_fl in split_names:
        sngl_var_file = sngl_fl.split('/')[-1]
        # variable short name:
        vn_short = sngl_var_file.split('_')[0]
        # look up corresponding long name:
        vn_long = var_df[var_df.short_name == vn_short].long_name.values[0]
        
        # construct file name in new structure
        if mode == 'forecast':
            assert system_num is not None, 'must define `system_num` keyword for mode == \'forecast\''
            
            sngl_var_file_in_struct = sngl_var_file.replace(
                vn_short,vn_long
            ).replace(
                '_{:}'.format(product),''
            ).replace(
                'latest',system_num
            ).replace(
                '.grib','.nc'
            )
        elif mode == 'hindcast':
            assert len(split_keys) > 1, 'must split hindcasts with variable name and hindcast year keywords'

            # indexingDate to desired format:
            idx_date = re.search('_(\d+).grib',sngl_var_file).groups()[0]

            # construct file name in new structure
            sngl_var_file_in_struct = sngl_var_file.replace(
                vn_short,vn_long
            ).replace(
                '_{:}'.format(mfin.PRODUCT),''
            ).replace(
                '.grib','.nc'
            ).replace(
                idx_date,'{Y:s}_{M:s}'.format(Y=idx_date[:4],M=idx_date[4:6])
            )

        # path to file in new structure:
        var_path = os.path.join(target_path,vn_long)
        # do conversion:
        targ_fl = os.path.join(var_path,sngl_var_file_in_struct)
        fc_convert_complete = sbp.run([
            'grib_to_netcdf',
            '-o',
            targ_fl,
            sngl_fl
        ])
        if fc_convert_complete.returncode == 0:
            print('{orig:s} successfully converted to {targ:s}. Removing original.'.format(orig=sngl_fl,targ=targ_fl))
            sbp.run(['rm',sngl_fl])

def split_grib(grib_file,mode='forecast',product_type='monthly',delete_input=False):
    """
    """

    if product_type == 'monthly':
        prod = mfin.PRODUCT
        hc_start,hc_end = mfin.hc_range[0], mfin.hc_range[-1]
    # elif product_type == 'subdaily':
    #     prod = sdfin.PRODCUT
    #     hc_start,hc_end = sdfin.hc_range[0], sdfin.hc_range[-1]


    model_ = [s for s in all_models if s in grib_file][0]
    month_ = grib_file.split('/')[-1].split('.')[0].split('_')[-1]

    if mode == 'forecast': 
        grib_split = grib_file.replace(prod,'[shortName]_{0:s}'.format(prod))
        split_complete = sbp.run(['grib_copy',grib_file,grib_split])
        # if the split was successful, remove the downloaded single file
    elif mode == 'hindcast':
        # split hindcasts in the same manner (must include hindcast year in split),  this can take up to 2 mins:
        if model_ in model_init_mode['lagged']:
            splt_date_key = '[indexingDate]' # want to sort by indexing date if model is initialized in lagged mode
        elif model_ in model_init_mode['burst']:
            splt_date_key = '[dataDate]'
        
        if os.path.exists(grib_file):
            print('splitting hindcast grib file')
            grib_split = grib_file.replace(
                prod,
                '[shortName]_{0:s}'.format(prod)
            ).replace(
                '{hcs:0<4d}-{hce:0<4d}_{mon:s}'.format(hcs = hc_start,hce = hc_end,mon=month_),
                splt_date_key
            )
            split_complete = sbp.run(['grib_copy',grib_file,grib_split])

    if (split_complete.returncode == 0) and delete_input:
        print('Splitting of {0:s} successful, removing.'.format(grib_file))
        sbp.run(['rm',grib_file])

    if mode == 'hindcast':
        return grib_split, splt_date_key
    else:
        return grib_split

if __name__ == '__main__':
    # get today's date:
    # init = datetime(2022,5,1)
    init = datetime.today()
    main(init)