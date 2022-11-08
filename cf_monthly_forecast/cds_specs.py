
model_init_mode = {
    'burst'     : ['cmcc','ecmwf','eccc','dwd','meteo_france'],
    'lagged'    : ['ukmo','jma','ncep']
}

# all available models:
all_models = ['ecmwf','meteo_france','dwd','cmcc','ukmo','ncep','eccc','jma']
# Note that the the last three models in this last are last on purpose. They aren't part of the MME as of now, so downloading them has low priority!

# maximum available lead hour for each system:  
last_lead_hour = dict(
    ecmwf           = 5160,
    meteo_france    = 5088,
    dwd             = 4392,
    cmcc            = 4416,
    ukmo            = 5160,
    ncep            = 5160,
    eccc            = 5136,
    jma             = 5160,
)

max_hour_4month = 2946

init_days_lagged = {
    'hindcast'  : {
        'ukmo'  : ['01','09','17','25'],
        'jma'   : [],
        'ncep'  : []
    },
    'forecast'  : {
        'ukmo'  : [],
        'jma'   : [],
        'ncep'  : []
    }
}
