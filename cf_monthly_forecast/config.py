# define some global parameters:

# email address to send unexpected program failures to:
email_address = 'owul@norceresearch.no'

# base directory of the project:
proj_base           = '/projects/NS9001K/owul/projects/cf_monthly_forecast'

# other relevant locations:
dirs = dict(
    SFE_forecast    = '/projects/NS9853K/DATA/SFE/Forecasts',
    test_data       = '{0:s}/data/raw'.format(proj_base),
    public          = '/projects/NS9853K/www/',
    figures         = '{0:s}/figures/'.format(proj_base)
)

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