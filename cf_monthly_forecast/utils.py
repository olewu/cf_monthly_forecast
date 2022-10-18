import smtplib
from cf_monthly_forecast.config import *
import re
import subprocess as sbp
import os
import cf_monthly_forecast.monthly_fc_input as mfin
import pandas as pd
from datetime import datetime

import numpy as np
import xarray as xr
from sklearn.neighbors import BallTree


def send_email(SUBJECT,TEXT,TO=[email_address],FROM = email_address):
    """
    send an email from email address defined in config.py to TO (must be list) with subject SUBJECT and message TEXT, both strings.
    """
    # Prepare actual message
    message = '''From: {0:s}
To: {1:s}
Subject: {2:s}

{3:s}
    '''.format(FROM, ', '.join(TO), SUBJECT, TEXT)

    # Send the mail
    server = smtplib.SMTP('localhost')
    server.sendmail(FROM, TO, message)
    server.quit()


def split_longname_into_varnames(dataset,var_key='variable'):
    """
    split the long_name attribute of a variable with key 'var_key' inside a dataset 'dataset'

    INPUT:
            dataset:    netCDF4._netCDF4.Dataset object as returned when opening netcdf file with Dataset function of the netCDF4 package
            var_names:  list of strings that represent the variable names, e.g. ['2m_temperature','total_precipitation']
    OUTPUT: 
            var_names_sorted:   list of variable names sorted by increasing index in the dataset, e.g. if '2m_temperature' is required from a dataset,
                                the index of '2m_temperature' in the output of this function can be used in the dataarray of the dataset

    """

    var_ix_all = []; var_names_all = []
    repeat = re.compile(r'(?P<start>[0-9]+): (?P<s>\w+)')
    for match in repeat.finditer(dataset.variables[var_key].long_name):
        var_ix_all.append(int(match.groups()[0])); var_names_all.append(match.groups()[1])

    # sort the list of variable names by increasing indices:
    var_names_sorted = [x for _, x in sorted(zip(var_ix_all, var_names_all), key=lambda pair: pair[0])]

    return var_names_sorted

def get_varnums(varlist,var_names):
    """
    get a dictionary that points from each required variable name in 'var_names' to the corresponding index in a list varlist

    INPUT: 
            varlist:    list of strings, each string a variable name, usually output of split_longname_into_varnames(dataset)
            var_names:  list or tuple of strings, each string a requested variable name.
                        If these are expected not to correspond exactly to elements in varlist,
                        define shorthands in the if statements of the function.

    OUTPUT:
            dct:        dictionary pointing from variable to index
    """

    dct = {}
    for key in var_names:
        if key in ['t2']:
            key_t = '2m_temperature'
        elif key in ['pr']:
            key_t = 'total_precipitation'
        elif key in ['wsp']:
            key_t = '10m_wind_speed'
        # ... can define arbitrary number of other shorthands here
        else:
            key_t = key
        
        dct[key] = varlist.index(key_t)
    
    return dct


def sysnum_from_grib(grib_file):
    """
    Infer the system number of a forecast in grib format from the file using grib_ls from ecCodes.
    
    -----WARNING-----
    Assumes that this number is constant for all fields in the grib file!
    -----------------

    INPUT:  
            grib_file:  path to an existing grib file (str)
    OUTPUT: value of system keyword in the grib file (str)
    """

    p = sbp.Popen(['grib_ls', '-p','system',grib_file], stdout=sbp.PIPE, stderr=sbp.PIPE)
    # retrieve output and error ('' if no error)
    out, err = p.communicate()
    # decode output from bytes to string:
    out_str = out.decode('utf-8')
    # search string for system number using regex:
    system_number = re.search('\d+',out_str.split('\n')[2]).group()

    return system_number

def derive_path(model,mode='monthly',create=True):
    
    if mode == 'monthly':
        temp_res = mfin.temp_res
        product = mfin.PRODUCT
    # elif mode == 'subdaily':
    #     temp_res = sdfin.temp_res
    #     product = sdfin.PRODUCT

    lookup_path = os.path.join(dirs['cds_data'],temp_res,product,model)
    # create the directory tree if it doesn't exist already:
    if (not os.path.exists(lookup_path)) and create:
        os.makedirs(lookup_path)
    
    return lookup_path

def get_missing_hindcast_fields(model,system,month,mode='monthly'):
    """
    INPUT:
            model       : modeling centre (str)
            system      : system number (str)
            initmonth   : initialization month (str)
            mode        : monthly of subdaily (does not exist yet...) (str)
    OUTPUT:
            list of missing variables
            list of missing years
            full path of where look-up was done
    """

    lookup_path = derive_path(model=model,mode=mode)

    missing_years   = []
    missing_vars    = []

    for var in reduce_vars(model,mode=mode):
        var_path = os.path.join(lookup_path,var)
        # check if the path for the variable exists at all and create if this is not the case
        if not os.path.exists(var_path):
            os.makedirs(var_path)
            missing_years.extend(list(mfin.hc_range))
            missing_vars.append(var)
        else:
            # filename for variable:
            hc_file = '{var:s}_{mod:s}_{sys:s}_?_{mon:s}.nc'.format(
                var     = var,
                mod     = model,
                mon     = month,
                sys     = system
            )
            
            # collect missing years:
            missing_years_var = []
            for yy in mfin.hc_range:
                year_file = hc_file.replace('_?_','_{:0<4d}_'.format(yy))
                year_file_path = os.path.join(var_path,year_file)
                if not os.path.exists(year_file_path):
                    missing_years_var.append(yy)
            if len(missing_years_var) > 0:
                print(var)
                missing_vars.append(var)
                missing_years.extend(missing_years_var)

    return missing_vars, missing_years


def reduce_vars(model,mode='monthly'):
    """
    """

    if mode == 'monthly':
        variables_df = mfin.variables_df
    # elif mode == 'subdaily':
    #     variables_df = sdfin.variables_df

    if model in ['ncep','jma']: # NCEP and JMA don't provide snowfall, so take these out the file list for request to succeed
        variables_reduced = [vv for vv in variables_df.long_name if vv not in ['snowfall']]
    else:
        variables_reduced = variables_df.long_name.to_list()

    return variables_reduced

def find_closest_gp(loc_dict,mode='any'):
    """
    returns lon/lat values that exist in the forecast files
    and that can be selected via xr.DataArray().sel()
    """
    
    # use an sst field to derive which grid points are ocean/land
    ds_sst = xr.open_dataset('/projects/NS9853K/DATA/SFE/Forecasts/forecast_production_sea_surface_temperature_2022_9.nc').sel(target_month=1).climatology_era

    mode = 'land'
    if mode == 'ocean':
        valid_np = np.array(~np.isnan(ds_sst),dtype=int)
    elif mode == 'land':
        valid_np = np.array(np.isnan(ds_sst),dtype=int)
    elif mode == 'any':
        valid_np = np.array(np.ones_like(ds_sst))
    else:
        print('choose one of (`any`,`ocean`,`land`) for `mode`')
        return None

    valid = xr.DataArray(
        valid_np,
        dims = ds_sst.dims,
        coords = ds_sst.coords
    )

    msk_stacked = valid.stack(index=['lat','lon'])
    msk_stacked = msk_stacked.where(msk_stacked == 1,drop=True)
    coords = np.deg2rad(np.stack([msk_stacked['lat'],msk_stacked['lon']],axis=-1))
    tree   = BallTree(coords,metric='haversine')
    # stack coordinates
    loc_coords = np.deg2rad(
        np.stack([ld for ldn,ld in loc_dict.items()])
    )
    k_indices = tree.query(loc_coords,return_distance=False).squeeze()
    lalo_close = msk_stacked.isel(index=k_indices).index.values

    return dict(zip(loc_dict.keys(), lalo_close))

def quadrant_probs(x_data,y_data,x_mean=0,y_mean=0):
    """
    Q1 upper right moving clockwise
    """

    if isinstance(x_data,xr.core.dataarray.DataArray):
        x_data = x_data.values
    if isinstance(y_data,xr.core.dataarray.DataArray):
        y_data = y_data.values
    if isinstance(x_mean,xr.core.dataarray.DataArray):
        x_mean = x_mean.values
    if isinstance(y_mean,xr.core.dataarray.DataArray):
        y_mean = y_mean.values

    total_ens = np.size(x_data)
    Q1_p = np.logical_and(x_data > x_mean, y_data > y_mean).sum()/total_ens * 100
    Q2_p = np.logical_and(x_data > x_mean, y_data < y_mean).sum()/total_ens * 100
    Q3_p = np.logical_and(x_data < x_mean, y_data < y_mean).sum()/total_ens * 100
    Q4_p = np.logical_and(x_data < x_mean, y_data > y_mean).sum()/total_ens * 100
    
    return (Q1_p,Q2_p,Q3_p,Q4_p)

def get_station_norm_1991_2020(variable,stat_name,month):
    """
    retrieve station normal 
    """
    # load csv:
    norm = pd.read_csv(
        os.path.join(dirs['station_norm'],'{0:s}_normals_station_norway_1991-2020.csv'.format(variable)),
        sep = ';',
        decimal = ',',
        index_col=0
    )
    # get station ID as defined in config
    stid = station_ids[stat_name]
    # get norwegian 3 letter month name:
    mon = MONTH_NAMES3_NO[month-1].lower()
    
    return norm[mon].loc[norm.index == stid].values[0]


def get_station_data(station_id):

    stat_normals = pd.read_csv(
        '/projects/NS9001K/owul/projects/cf_monthly_forecast/data/external/monthly_station_normals.csv',
        sep = ';',
        decimal = ','
    )

    station = 'SN' + str(station_id)
    timeix = [datetime.strptime(tt,'%m.%Y') for tt in stat_normals[stat_normals['Stasjon'] == station]['Tid(norsk normaltid)']]
    tp = np.array([np.nan if tt == '-' else np.float64(tt) for tt in stat_normals[stat_normals['Stasjon'] == station]['Nedbør (mnd)'].replace(',','.', regex=True)])
    t2 = np.array([np.nan if tt == '-' else np.float64(tt) for tt in stat_normals[stat_normals['Stasjon'] == station]['Middeltemperatur (mnd)'].replace(',','.', regex=True)])

    return xr.Dataset(
        data_vars = {
            '2m_temperature' : ('time',t2),
            'total_precipitation' : ('time',tp)
        },
        coords = {'time':timeix}
    )

    
def get_station_stats(station_id,start=1993,end=2016):
    
    xr_set = get_station_data(station_id)
    xr_subs = xr_set.sel(time=slice(str(start),str(end)))

    xr_subs_gr = xr_subs.groupby(xr_subs.time.dt.month)

    return xr_subs_gr.mean('time'), xr_subs_gr.std('time')

def predict_from_monthly_trend(station_id,pred_years,start=1991,end=2020):
    
    xr_set = get_station_data(station_id)
    xr_subs = xr_set.sel(time=slice(str(start),str(end)))

    xr_subs_gr = xr_subs.groupby(xr_subs.time.dt.month)

    trnd_prd_temp = []
    trnd_prd_prec = []
    index = []

    for mon,xrs in xr_subs_gr:
        pf_t2 = np.polyfit(np.arange(start,end+1),xrs['2m_temperature'],deg=1)
        trnd_prd_temp.append(np.polyval(pf_t2,np.array(pred_years)))

        pf_tp = np.polyfit(np.arange(start,end+1),xrs['total_precipitation'],deg=1)
        trnd_prd_prec.append(np.polyval(pf_tp,np.array(pred_years)))

        index.append(mon)

    # return trnd_prd_prec, trnd_prd_temp, index

    xr_trend_pred = xr.Dataset(
        data_vars = {
            '2m_temperature' : (('month','year'),np.array(trnd_prd_temp)),
            'total_precipitation' : (('month','year'),np.array(trnd_prd_temp))
        },
        coords = {
          'month' : ('month',index),
          'year' : ('year',pred_years)
        }
    )

    return xr_trend_pred
