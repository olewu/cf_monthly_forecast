# Operational downloading sequence for seasonal forecast monthly mean data

# Procedure (model by model):
# 1) Download grib file of the latest forecast (omit the model version keyword), all desired variables
# 2) infer sytem number from the returned file
# 3) check if hindcasts for the system and the specified month exist and download (grib, all variables, all hindcast years) if necessary (UKMO will always require a new download but should be ok since system number is also updated every year even if the model stays the same)
# 4) Split up the files (`grib_copy`) by variable and hindcast year
# 5) convert files to netcdf (`grib_to_netcdf`) 

import cdsapi
from glob import glob
import subprocess as sbp
import os
import sys
from datetime import datetime
import re
from cf_monthly_forecast.config import *
from cf_monthly_forecast.utils import sysnum_from_grib, get_missing_hindcast_fields, reduce_vars, derive_path, latest_sys_from_existing
from cf_monthly_forecast.conversion_utils import convert_grib_to_netcdf, split_grib
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

        idx_file = os.path.join(proj_base,'data/index/dl/','dl_complete_{0:s}_{1:s}-{2:s}_fc.ix'.format(MODEL,YEAR,MONTH))
        idx_file_hc = idx_file.replace('_fc.','_hc.')

        # add current model to input dict:
        input_dict['originating_centre'] = MODEL
        input_dict['variable'] = reduce_vars(MODEL,mode=mfin.temp_res)
        
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
        if not os.path.exists(idx_file):
            if not os.path.exists(outfile_fc):
                # note that this will currently execute as soon as `outfile_fc` does not exist, which also happens if the download was made and the file split!

                try:
                    # send request for forecast:
                    c.retrieve(
                        'seasonal-{0:s}-single-levels'.format(mfin.temp_res),
                        input_dict,
                        outfile_fc
                    )
                except Exception as xcpt:
                    print('{1:}: Could not download latest forecast for {0:s}.\nFailed with Exception {2:}'.format(MODEL,datetime.now(),xcpt))
                    # continue if download failed. Note that this will not make an attempt to download the corresponding 
                    # hindcasts, althought they might exist. The reason is that there is no automatic way (known to me) to 
                    # infer the system but to NOT pass it in the forecast request and then reading it off of the file.
                    # Doing the same with the hindcasts will not work since leaving 'system' empty will request ALL available systems.
                    continue
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
                grib_split_fc = split_grib(outfile_fc,mode='forecast',product_type=mfin.temp_res,delete_input=True)
            
            lookup_path = derive_path(MODEL,mode=mfin.temp_res)

            # do conversion of every single split file:
            convert_grib_to_netcdf(
                grib_split_fc,
                lookup_path,
                mode        = 'forecast',
                split_keys  = ['[shortName]'],
                prod_type   = mfin.temp_res,
                system_num  = SYSTEM
            )

            # if the loop ran to this point, create a file indicating that the forecast for the specified init date and model exists:
            sbp.run(['touch',idx_file])
        else:
            # need SYSTEM and lookup_path:
            SYSTEM,lookup_path = latest_sys_from_existing(MODEL,YEAR,MONTH)

        if not os.path.exists(idx_file_hc):
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
            missing_vars, missing_years = get_missing_hindcast_fields(MODEL,SYSTEM,MONTH,mode=mfin.temp_res)

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
                try:
                    c.retrieve(
                        'seasonal-{0:s}-single-levels'.format(mfin.temp_res),
                        input_dict_hc,
                        outfile_hc
                    )
                except Exception as xcpt:
                    print('{1:}: Could not download hindcasts for {0:s}.\nFailed with Exception \'{2:}\''.format(MODEL,datetime.now(),xcpt))
                    continue

                #----------------2.2) SPLIT BY VARIABLE & CONVERT TO NETCDF----------------#
                # split hindcasts in the same manner (must include hindcast year in split),  this can take up to 2 mins:
                grib_split_hc,splt_date_key = split_grib(outfile_hc,mode='hindcast',product_type=mfin.temp_res,delete_input=True)
                
                convert_grib_to_netcdf(
                    grib_split_hc,
                    lookup_path,
                    mode        = 'hindcast',
                    split_keys  = ['[shortName]',splt_date_key],
                    prod_type   = mfin.temp_res
                )
            
                # if the loop ran to this point, create a file indicating that the forecast for the specified init date and model exists:
            sbp.run(['touch',idx_file_hc])

        else:
            print('All requested hindcasts for {0:s} 1993-2016 already exist.'.format(MONTH))

    # check if all individual index files exist and make one final one that
    # indicates the bash script not to run:
    final_inv = glob(os.path.join(proj_base,'data/index/dl/','dl_complete_*_{0:s}-{1:s}_??.ix'.format(YEAR,MONTH)))
    # check that hindcast and forecast are there for every model:

    modinv_fc = sorted([re.search('ete_\w+_\d{4}',fi)[0][4:-5] for fi in final_inv if fi.split('.')[-2][-2:] == 'fc'])
    modinv_hc = sorted([re.search('ete_\w+_\d{4}',fi)[0][4:-5] for fi in final_inv if fi.split('.')[-2][-2:] == 'hc'])

    if modinv_fc == modinv_hc and modinv_fc == sorted(all_models):
        idx_file_final = os.path.join(proj_base,'data/index/dl/','dl_complete_{0:s}-{1:s}.ix'.format(YEAR,MONTH))
        sbp.run(['touch',idx_file_final])


if __name__ == '__main__':
    # get today's date:
    for fcy in range(2017,2023):
        init = datetime(fcy,11,1)
        # init = datetime.today()
        main(init)