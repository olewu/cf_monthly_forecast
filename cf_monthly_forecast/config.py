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