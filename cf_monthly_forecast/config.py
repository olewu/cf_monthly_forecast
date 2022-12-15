# define some global parameters:

import os
from pathlib import Path

# email address to send unexpected program failures to:
email_address = 'owul@norceresearch.no'

# base directory of the project:
proj_base           = str(Path(os.path.dirname(os.path.realpath(__file__))).parents[0])
data_base           = '/projects/NS9853K/' # '/nird/projects/NS9853K/' on the new NIRD-LDM system

# other relevant locations:
dirs = dict(
    SFE_summary     = os.path.join(data_base,'DATA/SFE/Forecasts'),
    SFE_monthly     = os.path.join(data_base,'DATA/SFE/cds_seasonal_forecast/monthly/monthly_mean/sfe'),
    public          = os.path.join(data_base,'www/'),
    cds_data        = os.path.join(data_base,'DATA/SFE/cds_seasonal_forecast'),
    senorge         = os.path.join(data_base,'DATA/senorge/'),
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
    wsp = '10m_wind_speed',
    msl = 'mean_sea_level_pressure',
    sst = 'sea_surface_temperature',
    snow = 'snowfall',
    u10m = '10m_u_component_of_wind',
    v10m = '10m_v_component_of_wind',
)

long_names = dict(
    t2 = dict(en='Temperature (2m)',no='Temperatur (2m)'),
    pr = dict(en='Precipitation',no='Nedbør'),
    wsp = dict(en='Wind Speed (10m)',no='Wind Hastighet (10m)'),
    msl = dict(en='Mean Sea Level Pressure', no='Midelere Bakketrykk'),
    sst = dict(en='Sea Surface Temperature', no='Sjøtemperatur'),
    snow = dict(en='Snowfall', no='Snøfall'),
    u10m = dict(en='Zonal Wind (10m)', no='Zonal Wind (10m)'),
    v10m = dict(en='Meridional Wind (10m)', no='Meridional Wind (10m)'),
)

units_plot = dict(
    t2 = '˚C',
    pr = 'mm', # accumulated over entire month
    wsp = 'm/s',
    msl = 'hPa',
    sst = '˚C',
    snow = '?',
    u10m = 'm/s',
    v10m = 'm/s',
)

units_tf_factor = dict(
    t2 = 1,
    pr = 1000, # ERA5 precip from monthly averaged files is in m/day, so for mm accumulated over month, need to multiply by 1000 to get to mm and by nr of days in resp month (external)
    wsp = 1, # 1 m/s = (1/1000 km) / (1/(60*60) h) = 3.6 km/h,
    msl = 1/100, # Pa to hPa
    sst = 1,
    snow = 1,
    u10m = 1,
    v10m = 1,
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