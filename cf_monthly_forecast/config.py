# define some global parameters:

import os

# email address to send unexpected program failures to:
email_address = 'owul@norceresearch.no'

# base directory of the project:
proj_base           = '/projects/NS9001K/owul/projects/cf_monthly_forecast'
data_base           = '/projects/NS9853K/DATA/SFE'

# other relevant locations:
dirs = dict(
    SFE_forecast    = os.path.join(data_base,'Forecasts'),
    test_data       = os.path.join(proj_base,'data/raw/'),
    public          = '/projects/NS9853K/www/',
    figures         = os.path.join(proj_base,'figures/'),
    inventory       = os.path.join(proj_base,'data/inventory/'),
    cds_data        = os.path.join(data_base,'cds_seasonal_forecast')
)

model_init_mode = {
    'burst'     : ['cmcc','ecmwf','eccc','dwd','meteo_france'],
    'lagged'    : ['ukmo','jma','ncep']
}

# all available models:
all_models = ['ukmo','ecmwf','meteo_france','dwd','cmcc','ncep','eccc','jma']
# Note that the the last three models in this last are last on purpose. They aren't part of the MME as of now, so downloading them has lower priority!

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