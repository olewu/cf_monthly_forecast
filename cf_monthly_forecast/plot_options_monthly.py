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
	'msl',
	# 'sst',
	# 'snow',
	# 'u10m',
	# 'v10m',
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
	'temperature_exceedance'		: np.linspace(0,100.,11),
	'total_precipitation_exceedance': np.linspace(0,100.,11),
	'ExceedQ33'						: np.linspace(0,100.,7),
	'ExceedQ50'						: np.linspace(0,100.,11),
	'ExceedQ67'						: np.linspace(0,100.,7),
	'ens_mean_anom'					: dict(
											t2 = dict(
												EUROPE = np.linspace(-2,2,11),
												GLOBAL = np.linspace(-2,2,11),
											),
											pr = dict(
												EUROPE = np.linspace(-30,30,11),
												GLOBAL = np.linspace(-100,100,11),
											),
											wsp = dict(
												EUROPE = np.linspace(-1.,1.,11),
												GLOBAL = np.linspace(-1.,1.,11),
											),
											msl = dict(
												EUROPE = np.linspace(-4.,4.,11),
												GLOBAL = np.linspace(-4.,4.,11),
											),
											sst = dict(
												EUROPE = np.linspace(-2.,2.,11),
												GLOBAL = np.linspace(-2.,2.,11),
											),
											snow = dict(
												EUROPE = np.linspace(-30,30,11),
												GLOBAL = np.linspace(-100,100,11),
											),
											u10m = dict(
												EUROPE = np.linspace(-1.,1.,11),
												GLOBAL = np.linspace(-1.,1.,11),
											),
											v10m = dict(
												EUROPE = np.linspace(-1.,1.,11),
												GLOBAL = np.linspace(-1.,1.,11),
											),
										)
}

cmapnames = {
	'ExceedQ33'						: {'t2':cm.oslo_r,'pr':cmo.turbid,'wsp':cm.grayC,'msl':cm.grayC,'sst':cm.oslo_r,'snow':cmo.turbid,'u10m':cm.grayC,'v10m':cm.grayC},
	'ExceedQ50'						: {'t2':cm.vik,'pr':cm.broc_r,'wsp':cm.roma_r,'msl':cm.roma_r,'sst':cm.vik,'snow':cm.broc_r,'u10m':cm.roma_r,'v10m':cm.roma_r},
	'ExceedQ67'						: {'t2':cm.lajolla,'pr':cm.bamako_r,'wsp':cm.acton_r,'msl':cm.acton_r,'sst':cm.lajolla,'snow':cm.bamako_r,'u10m':cm.acton_r,'v10m':cm.acton_r},
	'ens_mean_anom'					: {'t2':cm.vik,'pr':cmo.tarn,'wsp':cm.roma_r,'msl':cm.roma_r,'sst':cm.vik,'snow':cmo.tarn,'u10m':cm.roma_r,'v10m':cm.roma_r},
	'total_precipitation_exceedance': 'YlOrRd'
}

FMT = dict(
    t2 = '%.1f',
    pr = '%i',
    wsp = '%.1f',
    msl = '%.1f',
    sst = '%.1f',
    snow = '%i',
    u10m = '%.1f',
    v10m = '%.1f',
)