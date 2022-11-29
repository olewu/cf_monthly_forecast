import xarray as xr
import pandas as pd
from cf_monthly_forecast.config import *
import os

def senorge_clim(start_year,end_year,param='tg',aggr_period='month',aggr_meth='mean',savepath=None):
    
    filename = '{3:s}_senorge_{2:s}_clim_{4:s}_{0:d}-{1:d}.nc'.format(start_year,end_year,aggr_period,param,aggr_meth)
    path_to_file = os.path.join(savepath,filename)
    print('Checking for file {0:s}...'.format(path_to_file))

    if os.path.exists(path_to_file):
        print('... exists!')
        ds_clim = xr.open_dataset(path_to_file)
    else:
        print('... does not exist. Computing climatology...')
        data_dir = os.path.join(dirs['senorge'],param,'{0:s}_*.nc'.format(param))

        YEARS = [YE for YE in range(start_year,end_year+1)]

        ds_aggr = []
        for ye in YEARS:
            print('Processing: {0:d}'.format(ye))
            with xr.open_dataset(data_dir.replace('*','{:d}'.format(ye))) as ds:
                if aggr_period == 'week':
                    ds_grouped = ds.groupby(ds.time.dt.isocalendar()[aggr_period])
                elif aggr_period == 'month':
                    ds_grouped = ds.groupby(ds.time.dt.month)

                if aggr_meth == 'mean':
                    ds_aggr.append(ds_grouped.mean('time'))
                elif aggr_meth == 'median':
                    ds_aggr.append(ds_grouped.median('time'))
                elif aggr_meth == 'sum':
                    ds_aggr.append(ds_grouped.sum('time'))

        ds_aggr_allye = xr.concat(ds_aggr,dim=pd.Index(YEARS,name='year'))
        ds_clim = ds_aggr_allye.mean('year')

        if savepath is not None:
            ds_clim.to_netcdf(path_to_file)
            print('Climatology saved to {:s}'.format(path_to_file))
    
    return ds_clim