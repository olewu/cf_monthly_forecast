# Input to operational request to retrieve latest monthly aggregated seasonal forecasts via /notebooks/015_operational_download_sequence.py

# import pandas as pd

# temporal aggregation and corresponding product keyword for cds request:
temp_res = 'monthly'
PRODUCT = 'monthly_mean'

# Range of hindcast years:
hc_range = range(1993,2017)

var_names = {
    'long_name' : [
        '2m_temperature',
        'total_precipitation',
        'mean_sea_level_pressure',
        'sea_surface_temperature',
        'snowfall',
        '10m_wind_speed',
        '10m_u_component_of_wind',
        '10m_v_component_of_wind'
    ],
    'short_name' : [
        '2t',
        'tprate',
        'msl',
        'sst',
        'mtsfr',
        '10si',
        '10u',
        '10v'
    ]
}

long_names = {sn:ln for sn,ln in zip(var_names['short_name'],var_names['long_name'])}
short_names = {ln:sn for sn,ln in zip(var_names['short_name'],var_names['long_name'])}

# variables_df = pd.DataFrame(var_names,columns=['long_name','short_name'])

# Input to request that should remain constant for all forecast retrievals:
FORMAT          = 'grib'
LEADTIME_MONTH  = ['1', '2', '3','4', '5', '6']
AREA            = [89.5, -179.5, -89.5, 179.5]
GRID            = [1.0, 1.0]

input_dict = {
    'format'            : FORMAT,
    'product_type'      : PRODUCT,
    'leadtime_month'    : LEADTIME_MONTH,
    'area'              : AREA,
    'grid'              : GRID
}

# compression level for monthly output:
cmprss_lv = 5