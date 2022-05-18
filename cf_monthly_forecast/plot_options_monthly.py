# Arguments used for plotting in 002_forecast_plots.py
# comment out unwanted options

import numpy as np
from cmcrameri import cm
import cmocean.cm as cmo


#----------OPTIONAL (comment out single entries to omit)----------#

variables = (
	't2',
	'pr',
	'wsp',
)

langs = (
	# 'no',
	'en',
)

models = (
	# 'MeanTrend',
	'ExceedQ33',
	'ExceedQ67',
	'ExceedQ50',
	# 'temperature_exceedance',
	# 'total_precipitation_exceedance',
)


DOMAINS = [
	'EUROPE',
	'GLOBAL'
]


#---------PLOT SPECIFICS-----------#

cvs = {
	'MeanTrend'						: np.linspace(-1.6,1.6,17),
	'temperature_exceedance'		: np.linspace(0,100.,11),
	'total_precipitation_exceedance': np.linspace(0,100.,11),
	'ExceedQ33'						: np.linspace(0,100.,7),
	'ExceedQ50'						: np.linspace(0,100.,11),
	'ExceedQ67'						: np.linspace(0,100.,7)
}

cmapnames = {
	'ExceedQ33'						: {'t2':cm.oslo_r,'pr':cmo.turbid,'wsp':cm.grayC},
	'ExceedQ50'						: {'t2':cm.vik,'pr':cm.broc_r,'wsp':cm.roma_r},
	'ExceedQ67'						: {'t2':cm.lajolla,'pr':cm.bamako_r,'wsp':cm.acton_r},
	'temperature_exceedance'		: 'YlOrRd',
	'total_precipitation_exceedance': 'YlOrRd'
}
