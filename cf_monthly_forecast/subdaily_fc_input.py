# Input to operational request to retrieve latest monthly aggregated seasonal forecasts via /notebooks/015_operational_download_sequence.py

import pandas as pd
from cf_monthly_forecast.cds_specs import *

# temporal aggregation and corresponding product keyword for cds request:
temp_res = 'original'
PRODUCT = 'subdaily'

# Range of hindcast years:
hc_range = range(1993,2017)

var_names = {
    'long_name' : [
        '2m_temperature',
        'total_precipitation',
        'mean_sea_level_pressure',
        # 'sea_surface_temperature',
        # 'snowfall',
        # '10m_u_component_of_wind',
        # '10m_v_component_of_wind'
    ],
    'short_name' : [
        '2t',
        'tp', # note that these are 24h accumulated values, so precip file sizes will be a quarter of the 6hrly output
        'msl',
        # 'sst',
        # 'mtsfr',
        # '10u',
        # '10v'
    ]
}
# note that compared to the monthly output, the variables are reduced

variables_df = pd.DataFrame(var_names,columns=['long_name','short_name'])

# Input to request that should remain constant for all forecast retrievals:
FORMAT          = 'grib'
LEADTIME_HOUR   = [str(hh) for hh in range(0,max_hour_4month+1,6)]
AREA            = [89.5, -179.5, -89.5, 179.5]
GRID            = [1.0, 1.0]

input_dict = {
    'format'            : FORMAT,
    'leadtime_hour'     : LEADTIME_HOUR,
    'area'              : AREA,
    'grid'              : GRID
}

# compression level for (sub)daily output:
cmprss_lv = 5