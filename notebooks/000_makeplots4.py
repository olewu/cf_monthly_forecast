
import numpy as np
import sys
import matplotlib.pyplot as plt
from cf_monthly_forecast.ewkutils import SubplotFigureBase,TWOCOLUMN_WIDTH_INCHES,daysinmonth,FONTSIZE
from mpl_toolkits.basemap import Basemap
from scipy import interpolate
from netCDF4 import Dataset #,num2date
from cmcrameri import cm


class SubplotFigure(SubplotFigureBase):
	def __init__(self,**kw):
		super().__init__(**kw)
		self.letter_format = '%s'
		#self.letter_format = '(%s)'
		self.letter_fontsize = FONTSIZE+1
		#self.letter_fontweight = 'normal'
		self.letter_fontweight = 'bold'

vardesc = {
	'no':{'t2': 'Gjennomsnittlig temperatur','pr': 'Gjennomsnittlig nedbør'},
	'en':{'t2': 'Average temperature','pr': 'Average precipitation','wsp':'Average wind speed'}
}
units = {
	'no': {'t2': 'grader','pr': 'mm per dag'},
	'en': {'t2': 'deg C','pr': 'mm per day'}
}
cvs = {
	'MeanTrend': np.linspace(-1.6,1.6,17),
	'temperature_exceedance': np.linspace(0,100.,11),
	'total_precipitation_exceedance': np.linspace(0,100.,11),
	'ExceedQ33': np.linspace(0,100.,7),
	#'ExceedQ50': np.linspace(0,100.,7),
	'ExceedQ50': np.linspace(0,100.,11),
	'ExceedQ67': np.linspace(0,100.,7)
}
cmapnames = {
	#'ExceedQ33': 'GnBu',
	#'ExceedQ33': {'t2':'Blues','pr':'Reds'},
	'ExceedQ33': {'t2':'Blues','pr':'copper_r'},
	'ExceedQ50': {'t2':'RdBu_r','pr':'PuOr','wsp':'coolwarm'},
	#'ExceedQ50': {'t2':'RdBu_r','pr':'RdBu'},
	#'ExceedQ67': 'YlOrRd',
	#'ExceedQ67': {'t2':'Reds','pr':'Blues'},
	'ExceedQ67': {'t2':'Reds','pr':'Greens'},
	'temperature_exceedance': 'YlOrRd',
	'total_precipitation_exceedance': 'YlOrRd'
}
variables = (
	#'t2',
	#'pr',
	'wsp',
)
variablenumber = {
	't2':0,
	'pr':2,
	'wsp':5,
}
langs = (
	#'no',
	'en',
)
models = (
	#'MeanTrend',
	#'ExceedQ33',
	#'ExceedQ67',
	'ExceedQ50',
	#'temperature_exceedance',
	#'total_precipitation_exceedance',
)
FS = 9.
monthnames = {
	'no': ['Januar','Februar','Mars','April','Mai','Juni','Juli','August','September','Oktober','November','Desember'],
	'en': ['January','February','March','April','May','June','July','August','September','October','November','December']
}
nsplines = 4
init = False
initmonth = 1
inityear = 2022
fcmonth = 2
fcyear = 2022
GLOBAL = 'GLOBAL'
EUROPE = 'EUROPE'
#EUROPE = 'EUROPE_SMALL'
#area = EUROPE
#area = GLOBAL
isrelative = False
quarterly = False
season = {'en':'the 2021-22 winter','no':'vinteren 2021-22'}
datadir = '/Users/ewk/Data/sfe'

for variable in variables:

	if isrelative:
		filename = 'forecast_relative_to_2018_2021_6.nc4'
		figw_inches = TWOCOLUMN_WIDTH_INCHES*.6
	else:
		if quarterly:
			filename = '%s/forecast_quarterly_%i_%02d.nc4'%(datadir,inityear,initmonth)
		else:
			filename = '%s/forecast_%i_%02d.nc4'%(datadir,inityear,initmonth)
		figw_inches = TWOCOLUMN_WIDTH_INCHES*.8

	ds = Dataset(filename, mode='r')
	lon = ds.variables['lon'][:]
	lat = ds.variables['lat'][:]
	lon,lat = np.meshgrid(lon,lat)

	for area in (
		EUROPE,
		#GLOBAL,
	):

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
				# llcrnrlon = np.min(lon)+5.,
				# llcrnrlat = np.min(lat)+4.5,
				# urcrnrlon = np.max(lon)-.10,
				# urcrnrlat = np.max(lat)-3.5,
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
		#gpoints = np.nonzero(lon.ravel()>=-np.inf)[0]
		gweights = np.cos(np.radians(lat.ravel()[gpoints]))
		gweights /= np.sum(gweights)
		points = np.nonzero((lon.ravel()>=lon0)&(lon.ravel()<=lon1)&(lat.ravel()>=lat0)&(lat.ravel()<=lat1))[0]
		weights = np.cos(np.radians(lat.ravel()[points]))
		weights /= np.sum(weights)
		#print(len(points),len(lon.ravel()))
		#sys.exit()

		if nsplines:
			lon2 = np.linspace(lon[0,0],lon[0,-1],lon.shape[1]*nsplines)
			lat2 = np.linspace(lat[0,0],lat[-1,0],lat.shape[0]*nsplines)
			lon3,lat3 = np.meshgrid(lon2,lat2)
			xi,yi = bm(lon3,lat3)
		else:
			xi,yi = bm(lon,lat)
			xp,yp = bm(lon-.25,lat-.25)
		for model in models:
			a = None
			if quarterly:
				a = ds.variables[model][variablenumber[variable],:,:]
			if a is None:
				idx = fcmonth-initmonth-1
				if idx<0:
					idx += 12
				print(fcmonth,initmonth,idx)
				try:
					a = ds.variables[model][variablenumber[variable],idx,:,:]
				except:
					#raise
					a = ds.variables[model][idx,:,:]
			cv = cvs[model]
			ticks = cv
			fmt = '%.0f'
			#cmap = cm.lajolla
			try:
				cmapname = cmapnames[model][variable]
			except:
				cmapname = cmapnames[model]
			cmap = plt.get_cmap(cmapname,len(cv)-1)
			a *= 100.
			if model in ('ExceedQ33',):
				a = 100.-a

			# Compute area average:
			gavg = np.sum(a.ravel()[gpoints]*gweights)
			avg = np.sum(a.ravel()[points]*weights)
			print(model,avg)
			#sys.exit()

			#if model in ('ExceedQ50',):
			#	a[((a>40)&(a<60))] = np.nan
			#	cmap.set_bad('white')
			print(variable,np.min(a),np.max(a))
			for lang in langs:
				mstr = monthnames[lang][fcmonth-1]
				title = ''
				if model in ('ExceedQ67',):
					title = {
						'en': 'Probability of %s %i in the %s tercile (default = 33%%%s)'%(
							mstr,
							fcyear,
							{'t2':'warmest','pr':'wettest'}[variable],
							(', average = %i%%'%(avg+.5) if area==GLOBAL else '')
						)
					}[lang]
				elif model in ('ExceedQ50',):
					if quarterly:
						title = {
							'en': 'Estimated probability that %s'%(
								season[lang]
							)
						}[lang]
					else:
						title = {
							'en': 'Estimated probability that %s %i'%(
								mstr,
								fcyear
							)
						}[lang]
					if area==GLOBAL:
						t = ', global average: %i%%'%(avg+.5)
					else:
						t = ', average between %iN and %iN: %i%%'%(glat0,glat1,gavg+.5)
					title += {
						'en': ' will be %s than normal\n(default: 50%%%s)'%(
							{'t2':'warmer','pr':'wetter','wsp':'windier'}[variable],
							t
							#', reference = %i%% $^*$'%(gavg+.5)
							#(', average = %i%%'%(avg+.5) if area==GLOBAL else '')
						)
					}[lang]
				elif model in ('ExceedQ33',):
					title = {
						'en': 'Probability of %s %i in the %s tercile (default = 33%%%s)'%(
							mstr,
							fcyear,
							{'t2':'coldest','pr':'driest'}[variable],
							(', average = %i%%'%(avg+.5) if area==GLOBAL else '')
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
				# if model in ('MeanTrend'):
				# 	title = '%s: %s (%s) %s %s'%(
				# 		mstr,
				# 		#int(data['year'][0,0,midx]),
				# 		vardesc[lang][variable],
				# 		{'no':'avvik fra gj.snitt siste 25 år','en':'deviation from avg. last 25 years'}[lang],
				# 		{'no':'i','en':'in'}[lang],
				# 		units[lang][variable]
				# 	)
				# elif model[0]=='Q':
				# 	title = {
				# 		'no':'Sjanse for at %s blir varmere enn normalt siste 25 år'%mstr.lower(),
				# 		'en':'Chance that %s will be warmer than normal last 25 years'%mstr
				# 	}[lang]
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
					#nx = len(modelnames)+1
				)
				ax = fig.subplot(0)
				# a = None
				# mstr = []
				# ndays = 0
				# for i,midx in enumerate(midxs):
				# 	mstr.append(monthnames[lang][int(months[midx])-1])
				# 	ndays += daysinmonth(years[midx],months[midx])
				# 	b = data['comp_ano'][:,:,midx].T
				# 	if a is None:
				# 		a = np.empty([len(midxs)] + list(b.shape))
				# 	a[i,:,:] = b
				# a = np.mean(a,axis=0)
				#if variable=='pr':
				#	a *= ndays
				#mstr = ' '.join(mstr)
				if nsplines:
					#print(lon.shape,lat.shape,a.shape)
					f = interpolate.interp2d(lon[0,:], lat[:,0], a, kind='linear')
					a = f(lon2,lat2)
				spr = cv[-1]-cv[0]
				a[a<=cv[0]] = cv[0]+spr/1000.
				a[a>=cv[-1]] = cv[-1]-spr/1000.
				hatches = [None]*(len(cv)-1)
				# if len(cv)%2 > 0:
				# 	first = int((len(cv)-1)/2)-1
				# 	hatches[first:first+2] = '\\'
				plt.contourf(xi,yi,a,cv,cmap=cmap,vmin=cv[0],vmax=cv[-1],hatches=hatches)
				#plt.contour(xi,yi,a,[100./3,200./3],colors='w',linestyles='--',linewidths=1)
				# if model=='ExceedQ50':
				# 	plt.contour(xi,yi,a,[50],colors='w',linestyles='-',linewidths=2)
				#plt.pcolormesh(xp,yp,a,cmap=cmap,vmin=cv[0],vmax=cv[-1])#,shading='gouraud')
				#bm.drawcoastlines(linewidth=.35,color='w')
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
					#t += '\n%s'%{'no':'Partnere: Bjerknessenteret, NORCE,','en':'Partners: Bjerknes Center, NORCE,'}[lang]
					#t += '\n%s'%{'no':'Universitetet i Bergen, Nansensenteret','en':'University of Bergen, NERSC,'}[lang]
					#t += '\n%s'%{'no':'og Norsk regnesentral','en':'and the Norwegian Computing Center'}[lang]
					t += '\n%s:'%{'no':'Basert på data fra','en':'Based on data from'}[lang]
					#t += '\n%s'%{'no':'Bjerknessenteret (Norge)','en':'Bjerknes Center (Norway)'}[lang]
					t += '\nECMWF (%s)'%{'no':'Europa','en':'Europe'}[lang]
					t += '\nUK Met Office (%s)'%{'no':'Storbritannia','en':'UK'}[lang]
					t += '\nCMCC (%s)'%{'no':'Italia','en':'Italy'}[lang]
					t += '\nMétéo France (%s)'%{'no':'Frankrike','en':'France'}[lang]
					t += '\nDWD (%s)'%{'no':'Tyskland','en':'Germany'}[lang]
					t += '\n%s'%{'no':'Utarbeidet 16. novemver 2021','en':'Published 25 January 2022'}[lang]
					#t += '\n%s'%{'no':'Utarbeidet 20. oktober 2021','en':'Produced 20 October 2021'}[lang]
					#t += '\n%s'%{'no':'* ','en':'* average for %i$^\circ$N$-%i^\circ$N'}[lang]%(glat0,glat1)
					#t += '\n%s'%{'no':'Utarbeidet 21. september 2021','en':'Produced 21 September 2021'}[lang]
					#t += '\n%s'%{'no':'Utarbeidet 17. august 2021','en':'Produced 17 August 2021'}[lang]
					#t += '\n%s'%{'no':'Utarbeidet 15. juni 2021','en':'Produced 15 June 2021'}[lang]
					plt.text(0.01,.91,t,fontsize=FS-4,**tkw)
				plt.title(title,fontsize = FS-1)
				desc = 'Probability (%)'
				# if model[0]=='Q':
				# 	desc = {
				# 		'no':'Sannsynlighet (%)',
				# 		'en':'Probability (%)'
				# 	}[lang]
				rightmargin = 0
				if area in ('GLOBAL',):
					rightmargin = 0.05
				fig.draw_colorbar(
					fontsize=FS-1, 
					cmap = cmap, 
					vmin = cv[0], 
					vmax = cv[-1],
					desc = desc,
					ticks = ticks,
					rightmargin = rightmargin,
					fmt = fmt
				)
				filename = 'fc_%s_%s_%s_%s_%s'%(
					variable,
					'%02d'%fcmonth,
					model,
					#'_'.join(['%02d'%i for i in midxs]),
					area,
					lang
				)
				if quarterly:
					filename += '_q'
				plt.savefig(filename+'.png',dpi=300)
				#plt.show()
				#sys.exit(0)

plt.show()


