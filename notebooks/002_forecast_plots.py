#!

#--------------------IMPORT NECESSARY PACKAGES-------------------#

# OS interactions and calls:
import os
import subprocess as sbp
import sys

# project specific configurations:
from cf_monthly_forecast.config import dirs
import cf_monthly_forecast.forecast_file_parameters as ffp
import cf_monthly_forecast.plot_params_monthly as ppm

# data access
from netCDF4 import Dataset

# data processing
import numpy as np
from scipy import interpolate
from datetime import datetime,timedelta
import pandas as pd

# plotting
import matplotlib.pyplot as plt
from cf_monthly_forecast.vis_utils import TWOCOLUMN_WIDTH_INCHES,SubplotFigure
from mpl_toolkits.basemap import Basemap


#--------------------SOME INPUT--------------------#

# keep these to False for now:
isrelative = False
quarterly = False

# fontsize:
FS = 9.

# splines used for interpolation
nsplines = 4


#--------------------CHECK FOR EXISTENCE OF FORECAST FILE--------------------#

# get current date during time of running the script:
# today = datetime.today()
today = datetime(2022,4,15)
initmonth = today.month
inityear = today.year

# generate the expected name of the current forecast file:
if isrelative:
    filename = 'forecast_relative_to_2018_2021_6.nc4'
    figw_inches = TWOCOLUMN_WIDTH_INCHES*.6
else:
    if quarterly:
        filename = '{0:s}/forecast_quarterly_{1:s}_{2:s}.nc4'.format(dirs['SFE_forecast'],str(inityear).zfill(4),str(initmonth).zfill(2))
    else:
        filename = '{0:s}/forecast_{1:s}_{2:s}.nc4'.format(dirs['SFE_forecast'],str(inityear).zfill(4),str(initmonth).zfill(2))
    figw_inches = TWOCOLUMN_WIDTH_INCHES*.8

# Check for existence and abort if the file does not exist:
if not os.path.isfile(filename):
    print('Forecast file {0:s} does not exist!'.format(filename))
    sys.exit()


#--------------------MAKE A DIRECTORY FOR THE FIGURES--------------------#

# define where forecasts are located and where figures should be saved:
figdir = '{0:s}/monthly_fc/init_{1:s}-{2:s}/'.format(
    dirs['public'],str(inityear).zfill(4),str(initmonth).zfill(2)
)

# create a folder for the initialization if it doesn't already exist:
if not os.path.exists(figdir):
    sbp.call('mkdir {0:s}'.format(figdir),shell=True)


#--------------------LOAD FORECAST DATA--------------------#
# load netcdf:
ds = Dataset(filename, mode='r')
lon = ds.variables['lon'][:]
lat = ds.variables['lat'][:]
lon,lat = np.meshgrid(lon,lat)


#--------------------FORECAST MONTHS TO LOOP OVER--------------------#

# loop over forecast months & note that index 0 is forecast month 1!! (e.g. May init, index 0 has June monthly mean)
FCMONTHS = np.array(ds.variables['leadtime_month'][:],dtype=int)
FCYEARS = []
for mm in FCMONTHS:
    if mm >= initmonth:
        FCYEARS.append(inityear)
    else:
        FCYEARS.append(inityear+1)

# choose a subset of forecast months to plot:
subset = slice(0,None)
FCMONTH = FCMONTHS[subset]
FCYEAR = FCYEARS[subset]


#--------------------GENERATE FORECAST PROBABILITY PLOTS--------------------#

# loop over first 5 forecast months:
for fcmonth,fcyear in zip(FCMONTH,FCYEAR):

    # loop over available meteorlogical variables:
	for variable in ppm.variables:

        # loop over domains
		for area in ppm.DOMAINS:

			if area == 'EUROPE_SMALL':
				lon0 = 0
				lon1 = 30
				lat0 = 54
				lat1 = 71.5
				bm = Basemap(
					resolution = 'i', 
					projection = 'gall',
					llcrnrlon = 0,
					llcrnrlat = 54,
					urcrnrlon = 30,
					urcrnrlat = 71.5,
					fix_aspect = False
				)
				aspectratio = 1.1
			elif area == 'EUROPE':
				lon0 = -20
				lon1 = 50
				lat0 = 35
				lat1 = 72
				bm = Basemap(
					resolution = 'l', 
					projection = 'gall',
					llcrnrlon = -20.,
					llcrnrlat = 35.,
					urcrnrlon = 50.,
					urcrnrlat = 72.,
					fix_aspect = False
				)
				aspectratio = 1.5
			elif area == 'GLOBAL':
				lon0 = -180
				lon1 = 180
				lat0 = -90
				lat1 = 90
				bm = Basemap(projection='moll',lon_0=0,resolution='c')
				aspectratio = 2.05

			# weights:
			glat0 = 40
			glat1 = 70
			gpoints = np.nonzero((lat.ravel()>=glat0)&(lat.ravel()<=glat1))[0]
			gweights = np.cos(np.radians(lat.ravel()[gpoints]))
			gweights /= np.sum(gweights)
			points = np.nonzero((lon.ravel()>=lon0)&(lon.ravel()<=lon1)&(lat.ravel()>=lat0)&(lat.ravel()<=lat1))[0]
			weights = np.cos(np.radians(lat.ravel()[points]))
			weights /= np.sum(weights)

			if nsplines:
				lon2 = np.linspace(lon[0,0],lon[0,-1],lon.shape[1]*nsplines)
				lat2 = np.linspace(lat[0,0],lat[-1,0],lat.shape[0]*nsplines)
				lon3,lat3 = np.meshgrid(lon2,lat2)
				xi,yi = bm(lon3,lat3)
			else:
				xi,yi = bm(lon,lat)
				xp,yp = bm(lon-.25,lat-.25)
			for model in ppm.models:
				a = None
				if quarterly:
					a = ds.variables[model][ffp.variablenumber[variable],:,:]
				if a is None:
					idx = fcmonth-initmonth-1
					if idx<0:
						idx += 12
					print(fcmonth,initmonth,idx)
					try:
						a = ds.variables[model][ffp.variablenumber[variable],idx,:,:]
					except:
						#raise
						a = ds.variables[model][idx,:,:]
				cv = ppm.cvs[model]
				ticks = cv
				fmt = '%.0f'
				try:
					cmapname = ppm.cmapnames[model][variable]
				except:
					cmapname = ppm.cmapnames[model]
				cmap = plt.get_cmap(cmapname,len(cv)-1)
				a *= 100.
				if model in ('ExceedQ33',):
					a = 100.-a

				# Compute area average:
				gavg = np.sum(a.ravel()[gpoints]*gweights)
				avg = np.sum(a.ravel()[points]*weights)
				print(model,avg)
				print(variable,np.min(a),np.max(a))

                # loop over languages:
				for lang in ppm.langs:
					mstr = ffp.monthnames[lang][fcmonth-1]
					title = ''
					if model in ('ExceedQ67',):
						title = {
							'en': 'Probability of %s %i in the %s tercile (default = 33%%%s)'%(
								mstr,
								fcyear,
								{'t2':'warmest','pr':'wettest','wsp':'windiest'}[variable],
								(', average = %i%%'%(avg+.5) if area=='GLOBAL' else '')
							)
						}[lang]
					elif model in ('ExceedQ50',):
						if quarterly:
							title = {
								'en': 'Estimated probability that %s'%(
									ffp.season[lang]
								)
							}[lang]
						else:
							title = {
								'en': 'Estimated probability that %s %i'%(
									mstr,
									fcyear
								)
							}[lang]
						if area == 'GLOBAL':
							t = ', global average: %i%%'%(avg+.5)
						else:
							t = ', average between %iN and %iN: %i%%'%(glat0,glat1,gavg+.5)
						title += {
							'en': ' will be %s than normal\n(default: 50%%%s)'%(
								{'t2':'warmer','pr':'wetter','wsp':'windier'}[variable],
								t
							)
						}[lang]
					elif model in ('ExceedQ33',):
						title = {
							'en': 'Probability of %s %i in the %s tercile (default = 33%%%s)'%(
								mstr,
								fcyear,
								{'t2':'coldest','pr':'driest','wsp':'calmest'}[variable],
								(', average = %i%%'%(avg+.5) if area=='GLOBAL' else '')
							)
						}[lang]
					elif model in ('temperature_exceedance',):
						title = {
							'en': 'Probability that July 2021 will be warmer than July 2018'
						}[lang]
					elif model in ('total_precipitation_exceedance',):
						title = {
							'en': 'Probability that July 2021 will be drier than July 2018'
						}[lang]

                    # initialize the figure:
					fig = SubplotFigure(
						figw_inches = figw_inches,
						aspectratio = aspectratio,
						marginleft_inches = 0.05,
						marginright_inches = 0.05,
						margintop_inches = 0.45,
						marginbottom_inches = 0.05,
						cbar_height_inches = .15,
						cbar_bottompadding_inches = .25,
						cbar_toppadding_inches = .05,
						cbar_width_percent = 95.
					)
                    # add subplot:
					ax = fig.subplot(0)
					if nsplines:
						print('linearly interpolating data to {0:d}x the resolution'.format(nsplines))
						f = interpolate.interp2d(lon[0,:], lat[:,0], a, kind='linear')
						a = f(lon2,lat2)
					spr = cv[-1]-cv[0]
					a[a<=cv[0]] = cv[0]+spr/1000.
					a[a>=cv[-1]] = cv[-1]-spr/1000.
					levels = np.arange(cv[0],cv[-1])
					hatches = [None]*(len(cv)-1)
					# Plot probabilities:
					cf = ax.contourf(xi,yi,a,cv,cmap=cmap,vmin=cv[0],vmax=cv[-1],hatches=hatches)
					bm.drawcoastlines(linewidth=.5)
					bm.drawcountries(linewidth=.35,color='.5')
					if not area in ('GLOBAL',):
						tkw = {
							'horizontalalignment':'left',
							'verticalalignment':'top',
							'transform':ax.transAxes
						}
						t = '%s Seasonal Forecasting Engine'%{'no':'Varsel fra','en':'Forecast from'}[lang]
						t += '\n%s Climate Futures'%{'no':'og','en':'and'}[lang]
						plt.text(0.01,.99,t,fontweight='bold',fontsize=FS-2,**tkw)
						t = {'no':'Finansiert av Forskningsrådet','en':'Funded by the Research Council of Norway'}[lang]
						t += '\n%s:'%{'no':'Basert på data fra','en':'Based on data from'}[lang]
						t += '\nECMWF (%s)'%{'no':'Europa','en':'Europe'}[lang]
						t += '\nUK Met Office (%s)'%{'no':'Storbritannia','en':'UK'}[lang]
						t += '\nCMCC (%s)'%{'no':'Italia','en':'Italy'}[lang]
						t += '\nMétéo France (%s)'%{'no':'Frankrike','en':'France'}[lang]
						t += '\nDWD (%s)'%{'no':'Tyskland','en':'Germany'}[lang]
						t += '\n{0:s} {1:d}. {2:s}. {3:d}'.format({'no':'Utarbeidet','en':'Published'}[lang],today.day,ffp.monthnames[lang][today.month-1],today.year)
						plt.text(0.01,.91,t,fontsize=FS-4,**tkw)
					plt.title(title,fontsize = FS-1)
					desc = 'Probability (%)'
					rightmargin = 0
					if area in ('GLOBAL',):
						rightmargin = 0.05
					fig.draw_colorbar(
						mappable = cf,
						fontsize=FS-1, 
						cmap = cmap, 
						vmin = cv[0], 
						vmax = cv[-1],
						desc = desc,
						ticks = ticks,
						rightmargin = rightmargin,
						fmt = fmt
					)
					filename = 'fc_{0:s}_{1:s}_{2:s}_{3:s}_{4:s}'.format(
						variable,
						str(fcmonth).zfill(2),
						model,
						area,
						lang
					)
					if quarterly:
						filename += '_q'
					fig.fig.savefig('{0:s}{1:s}.png'.format(figdir,filename),dpi=300)
					plt.close(fig.fig)