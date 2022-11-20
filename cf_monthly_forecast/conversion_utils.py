from glob import glob
import re
import subprocess as sbp

from cf_monthly_forecast.config import *
import cf_monthly_forecast.monthly_fc_input as mfin
import cf_monthly_forecast.subdaily_fc_input as sdfin


def convert_grib_to_netcdf(split_files,target_path,mode,split_keys=['[shortName]'],prod_type='monthly',system_num=None,compression_level=0):
    """

    """

    if prod_type == 'monthly':
        product = mfin.PRODUCT
        long_names = mfin.long_names
    elif prod_type == 'subdaily':
        product = sdfin.PRODUCT
        long_names = sdfin.long_names

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
        vn_long = long_names[vn_short]
        
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
        elif mode == 'hindcast' and prod_type == 'monthly':
            assert len(split_keys) > 1, 'must split hindcasts with variable name and hindcast year keywords'

            # indexingDate to desired format:
            idx_date = re.search('_(\d+).grib',sngl_var_file).groups()[0]

            # construct file name in new structure
            sngl_var_file_in_struct = sngl_var_file.replace(
                vn_short,vn_long
            ).replace(
                '_{:}'.format(product),''
            ).replace(
                '.grib','.nc'
            ).replace(
                idx_date,'{Y:s}_{M:s}'.format(Y=idx_date[:4],M=idx_date[4:6])
            )
        elif mode == 'hindcast' and prod_type == 'subdaily':
            
            # construct file name in new structure
            sngl_var_file_in_struct = sngl_var_file.replace(
                vn_short,vn_long
            ).replace(
                '_{:}'.format(product),''
            ).replace(
                '.grib','.nc'
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

            if compression_level != 0:
                cmprs_fl = targ_fl.replace('.nc','_cmprssd.nc')
                print('compressing {0:s}'.format(targ_fl))
                cmprss = sbp.run([
                    'nccopy',
                    '-k', '4', '-s', '-d', str(compression_level),
                    targ_fl,
                    cmprs_fl
                ])
                if cmprss.returncode == 0:
                    # remove uncompressed file if compression was successful:
                    sbp.run(['rm',targ_fl])
                    # rename compressed file
                    sbp.run(['mv',cmprs_fl,targ_fl])

def split_grib(grib_file,mode='forecast',product_type='monthly',delete_input=False):
    """
    """

    if product_type == 'monthly':
        prod = mfin.PRODUCT
        hc_start,hc_end = mfin.hc_range[0], mfin.hc_range[-1]
    elif product_type == 'subdaily':
        prod = sdfin.PRODUCT
        hc_start,hc_end = sdfin.hc_range[0], sdfin.hc_range[-1]


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
