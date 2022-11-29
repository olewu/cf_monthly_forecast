# define some global parameters:

import os

# email address to send unexpected program failures to:
email_address = 'owul@norceresearch.no'

# base directory of the project:
proj_base           = '/projects/NS9001K/owul/projects/cf_monthly_forecast'
data_base           = '/projects/NS9853K/'

# other relevant locations:
dirs = dict(
    SFE_summary     = os.path.join(data_base,'DATA/SFE/Forecasts'),
    SFE_monthly     = os.path.join(data_base,'DATA/SFE/cds_seasonal_forecast/monthly/monthly_mean/sfe'),
    public          = os.path.join(data_base,'www/'),
    cds_data        = os.path.join(data_base,'DATA/SFE/cds_seasonal_forecast'),
    senorge         = '/projects/NS9853K/DATA/senorge/',
    test_data       = os.path.join(proj_base,'data/raw/'),
    station_norm    = os.path.join(proj_base,'data/external/'),
    processed       = os.path.join(proj_base,'data/processed/'),
    figures         = os.path.join(proj_base,'figures/'),
    inventory       = os.path.join(proj_base,'data/inventory/'),
)

model_init_mode = {
    'burst'     : ['cmcc','ecmwf','eccc','dwd','meteo_france'],
    'lagged'    : ['ukmo','jma','ncep']
}

# all available models:
all_models = ['ecmwf','meteo_france','dwd','cmcc','ukmo','ncep','eccc','jma']
# Note that the the last three models in this last are last on purpose. They aren't part of the MME as of now, so downloading them has low priority!

# system numbers assigned by Alex in production files:
dt_systems_lookups = {
    1: "cmcc",
    2: "dwd",
    3: "ecmwf",
    4: "meteo_france",
    5: "ukmo",
    6: "bccr",
}

# map short names to long names:
file_key = dict(
    t2 = '2m_temperature',
    pr = 'total_precipitation',
    wsp = '10m_wind_speed'
)

long_names = dict(
    t2 = dict(en='Temperature (2m)',no='Temperatur (2m)'),
    pr = dict(en='Precipitation',no='Nedbør'),
    wsp = dict(en='Wind Speed (10m)',no='wind hastighet (10m)')
)

units_plot = dict(
    t2 = '˚C',
    pr = 'mm', # accumulated over entire month
    wsp = 'm/s'
)

units_tf_factor = dict(
    t2 = 1,
    pr = 1000, # ERA5 precip from monthly averaged files is in m/day, so for mm accumulated over month, need to multiply by 1000 to get to mm and by nr of days in resp month (external)
    wsp = 1 # 1 m/s = (1/1000 km) / (1/(60*60) h) = 3.6 km/h
)

city_coords_lalo = {
    'Bergen'    : [60.389, 5.33],
    'Oslo'      : [59.913,10.739],
    'Trondheim' : [63.43, 10.393],
    'Tromsø'    : [69.683,18.943]
}

station_ids = {
    'Bergen'    : 50540,
    'Oslo'      : 18700,
    'Trondheim' : 68125,
    'Tromsø'    : 90450
}

MONTH_NAMES3 = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
MONTH_NAMESF = ['January','February','March','April','May','June','July','August','September','October','November','December']
MONTH_NAMES3_NO = ['Jan','Feb','Mar','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Des']
MONTH_NAMESF_NO = ['Januar','Februar','Mars','April','Mai','Juni','Juli','August','September','Oktober','November','Desember']