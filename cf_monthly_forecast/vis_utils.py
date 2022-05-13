
from matplotlib.colorbar import ColorbarBase
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np
import traceback
from datetime import date, datetime, timedelta
import pickle
from scipy import interpolate
import calendar
from matplotlib.colors import ListedColormap
# from localsettings import HOMEDIR
import sys

DPI = 150
FONTSIZE = 9
REARTH = 6.371e6
TWOCOLUMN_WIDTH_INCHES = 6.5
ONECOLUMN_WIDTH_INCHES = 3.17
LETTERS = 'abcdefghijklmnopqrstuvxyzabcdefghijklmnopqrstuvxyz'
CACHE_DIR = '/Users/ewk/Sync/cache/python/wrftools'

C0 = '#1f77b4'
C1 = '#ff7f0e'
C2 = '#2ca02c'
C3 = '#d62728'
C4 = '#9467bd'
C5 = '#8c564b'
C8 = '#bcbd22'
C9 = '#17becf'

monthnames = {m: date(year=2000, month=m, day=1).strftime('%b') for m in range(1,13)}
longmonthnames = {m: date(year=2000, month=m, day=1).strftime('%B') for m in range(1,13)}

def psave(a,filename):
	f = open(filename,'wb')
	pickle.dump(a,f)
	f.close()
	
def hideaxes(ax):
	ax.spines['top'].set_visible(False)
	ax.spines['right'].set_visible(False)
	ax.spines['bottom'].set_visible(False)
	ax.spines['left'].set_visible(False)

def pimp_axes(ax):
	ax.tick_params(labelsize=FONTSIZE-2,direction='inout')
	ax.yaxis.set_ticks_position('both')

def ecdf(sample):
    # convert sample to a numpy array, if it isn't already
    sample = np.atleast_1d(sample)
    # find the unique values and their corresponding counts
    quantiles, counts = np.unique(sample, return_counts=True)
    # take the cumulative sum of the counts and divide by the sample size to
    # get the cumulative probabilities between 0 and 1
    cumprob = np.cumsum(counts).astype(np.double) / sample.size
    return quantiles, cumprob

def daysinmonth(year,month):
	return calendar.monthrange(int(year),int(month))[1]

def spline(x,y,xnew):
	tck = interpolate.splrep(x, y, s=0)
	ynew = interpolate.splev(xnew, tck, der=0)
	return ynew

def set_tick_params(ax = None, labelsize = None):
	if ax is None:
		ax = plt.gca()
	if labelsize is None:
		labelsize = FONTSIZE-2
	ax.tick_params(labelsize=labelsize,tick2On=False,tickdir='out',width=.75)

#----------------------------------------------------------------------------
#from quikscat_daily_v4 import QuikScatDaily
#from matplotlib import cm

missing = -999.

def get_quikscat_date(dt): 
	if dt.hour < 1:
		dt -= timedelta(hours=24)
	if dt.hour>12 or dt.hour<1:
		timeofday = 'evening'
	else:
		timeofday = 'morning'
	return dt.date(), timeofday


# def get_quikscat(
# 	dt = None, 
# 	timeofday = None
# ): 

# 	filename = '/Users/ewk/Sync/Data/QuikSCAT/qscat_%sv4.gz' %dt.strftime('%Y%m%d')

# 	dataset = QuikScatDaily(filename, missing=missing)
# 	if not dataset.variables: 
# 		sys.exit('file not found')

# 	iasc = (1 if timeofday == 'evening' else 0)
# 	wspdname = 'windspd'
# 	wdirname = 'winddir'

# 	# here is the data I will use:
# 	wspd = dataset.variables[wspdname][iasc,:,:]
# 	#wdir = dataset.variables[wdirname][iasc,:,:]
# 	land = dataset.variables['land'][iasc,:,:]
# 	gmt = dataset.variables['mingmt'][iasc,:,:]

# 	# get lon/lat:
# 	lon = dataset.variables['longitude']
# 	lat = dataset.variables['latitude']
# 	#print lon[:100]
# 	#raise
# 	# lon -= .5*(lon[1]-lon[0])
# 	# lat -= .5*(lat[1]-lat[0])
# 	lon,lat = np.meshgrid(lon,lat)

# 	#print lon.min(), lon.max(), lat.min(), lat.max()
# 	#raise
# 	lon[lon>180] -= 360
# 	I = np.nonzero((lat[:,0]>=45)&(lat[:,0]<=90))[0]
# 	J = np.nonzero((lon[0,:]>=-70)&(lon[0,:]<=60))[0]
# 	J = J[np.argsort(lon[0,J])]
# 	ix = np.ix_(I,J)

# 	return {
# 		'mingmt': gmt[ix],
# 		'lon': lon[ix],
# 		'lat': lat[ix],
# 		'wspd': wspd[ix],
# 		'land': land[ix]
# 	}

def tdhours(td):
	return (td.days * 24. + td.seconds / 3600.)


def find_closest(lon0, lat0, lon, lat):
	lat0r = np.radians(lat0)
	lon0r = np.radians(lon0)
	lat1r = np.radians(lat)
	lon1r = np.radians(lon)
	dlatr=lat1r-lat0r
	dlonr=lon1r-lon0r
	dist = np.sin(dlatr/2)**2 + np.cos(lat0r) * np.cos(lat1r) * np.sin(dlonr/2)**2
	return np.argsort(dist)[0]

def distance_between_two_points(lon0r, lat0r, lon1r, lat1r, km = True):
	dlatr=lat1r-lat0r
	dlonr=lon1r-lon0r
	a = np.sin(dlatr/2)**2 + np.cos(lat0r) * np.cos(lat1r) * np.sin(dlonr/2)**2
	return 2. * 6371. * np.arcsin(np.sqrt(a))
				
def reg_m(y, x):
	ones = np.ones(len(x[0]))
	X = sm.add_constant(np.column_stack((x[0], ones)))
	for ele in x[1:]:
		X = sm.add_constant(np.column_stack((ele, X)))
	#results = sm.OLS(y, X).fit(cov_kwds={'alpha': 0.01})
	results = sm.OLS(y, X).fit()
	return results

def get_default_colors():
	prop_cycle = plt.rcParams['axes.prop_cycle']
	return prop_cycle.by_key()['color']

def get_colors_from_cmap(num_colors, name = "gist_stern_r"):
	from matplotlib.pylab import get_cmap
	cm = get_cmap(name)
	I = np.arange(num_colors) / (num_colors-1.)
	#print I
	#raise
	#return [cm((1.*i)/num_colors) for i in range(num_colors)]
	return [cm(i) for i in I]

def get_beaufort_colormap():
	colors = [
		[98,0,2],
		[199,0,10],
		[254,48,19],
		[231,168,32],
		[255,238,45],
		[255,219,91],
		[166,255,184]
	]
	return matplotlib.colors.ListedColormap(np.array(colors)/255., name='beaufort'), colors

def compute_gradient(a, lon, lat):
	#print lon[0,:]
	lon[lon>=180] -= 360.
	J = np.argsort(lon[0,:])
	lon = lon[:,J]
	#print a[0,10,:5]
	a = a[:,:,J]
	dlon = lon[0,1] - lon[0,0]
	dlat = lat[1,0] - lat[0,0]
	#print dlon, dlat
	#print lon[0,:]

	# dx in m:
	dx = 2. * np.cos(np.radians(lat)) * REARTH * np.pi / 360. * dlon
	#print dx[:,0]
	#print lat[:,0]
	# dy in m:
	dy = 2 * REARTH * np.pi / 360. * dlat
	#print dy
	#print dx, dy
	#raise

	# da / dx first:
	dadx = np.ones(a.shape) * np.nan
	dadx[:,:,1:-1] = 0.5 * (a[:,:,2:] - a[:,:,:-2])
	if (lon[0,-1] + dlon + lon[0,0]) < 0.5:
		dadx[:,:,0] = 0.5 * (a[:,:,1] - a[:,:,-1])
		dadx[:,:,-1] = 0.5 * (a[:,:,0] - a[:,:,-2])
	else:
		dadx[:,:,0] = a[:,:,1] - a[:,:,0]
		dadx[:,:,-1] = a[:,:,-1] - a[:,:,-2]
	dadx /= dx

	# da/dy:
	dady = np.ones(a.shape) * np.nan
	dady[:,1:-1,:] = (a[:,2:,:] - a[:,:-2,:]) / (2.*dy)
	dady[:,0,:] = (a[:,1,:] - a[:,0,:]) / dy
	dady[:,-1,:] = (a[:,-1,:] - a[:,-2,:]) / dy

	return (dadx, dady,)

	#print a[0,10,:5]
	#print a.shape
	#print lon[0,:]

def _interp(lon, lat, xr, yr):
	sz = np.prod(lon.shape)
	# Convert to radians and make 1D
	lonr = np.radians(lon).reshape((sz,))
	latr = np.radians(lat).reshape((sz,))
	dlatr=yr[np.newaxis,:]-latr[:,np.newaxis]
	dlonr=xr[np.newaxis,:]-lonr[:,np.newaxis]
	# Compute distance:
	b = np.sin(dlatr/2)**2 + np.cos(latr[:,np.newaxis]) * np.cos(yr[np.newaxis,:]) * np.sin(dlonr/2)**2
	b = 2. * 6371. * np.arcsin(np.sqrt(b))
	# Pick out 4 closest grid points for each point on the circle
	I = list(np.ogrid[[slice(x) for x in b.shape]])
	I[0] = b.argsort(0)[:4,:]
	c = b[I]
	# Create weights:
	w = np.empty(c.shape)
	# Just in case some grid points are really close, use weight 1:
	K = (c[0,:]<0.1*c[1,:])
	if np.sum(K)>0:
		w[:,K] = np.array([1., 0., 0., 0.])[:,np.newaxis]
	# Now the normal points:
	K = (~K)
	# Weight by inverse of distance:
	w[:,K] = c[:,K]**(-1)
	# Normalize to 1:
	w[:,K] /= np.sum(w[:,K], axis=0)
	return w, I, sz

def interpolate_to_grid2(a, lon, lat, xr, yr, param = None):
	print("Finding weights...")
	w, I, sz = _interp(lon, lat, xr, yr)
	a = a.reshape((a.shape[0], sz,))
	oo = np.ones(xr.shape)
	ret = np.empty((a.shape[0], xr.shape[0],))
	prev = 0
	print("Applying weights...")
	for j in range(a.shape[0]):
		perc = int(100.*(j+1.)/a.shape[0]+.5)
		if perc >= prev + 10:
			prev = perc-perc%10
			print("%i%%..."%prev)
		c = a[j,:][:,np.newaxis] * oo
		ret[j,:] = np.sum(c[I]*w, axis=0)
	return ret

def interpolate_simple(a, lon0, lat0, lon1, lat1):
	sz = np.prod(lon1.shape)
	xr = np.radians(lon1.reshape((sz,)))
	yr = np.radians(lat1.reshape((sz,)))
	b = interpolate_to_grid([a], lon0, lat0, xr, yr)
	return b[0]

def interpolate_between_grids(a, lon0, lat0, lon1, lat1):
	sz = np.prod(lon1.shape)
	xr = np.radians(lon1.reshape((sz,)))
	yr = np.radians(lat1.reshape((sz,)))
	b = interpolate_to_grid2(a, lon0, lat0, xr, yr)
	b = b.reshape(a.shape)
	return b

def interpolate_to_grid(aa, lon, lat, xr, yr, param = None):
	w, I, sz = _interp(lon, lat, xr, yr)
	ret = []
	for a in aa:
		a = a.reshape((sz,))
		c = a[:,np.newaxis] * np.ones(xr.shape)
		ret.append(np.sum(c[I]*w, axis=0))
	return ret

def running_mean(x, N):
	window = np.ones(int(N))/float(N)
	return np.convolve(x, window, 'valid')
	#return np.convolve(x, window, 'same')
	
class SubplotFigureBase(object):

	def __init__(self, 
		figw_inches = None, 
		figh_inches = None,
		nx = None, 
		ny = None, 
		nbr_of_panels = None,
		axw_inches = None,
		axh_inches = None, 
		aspectratio = 1.0,
		figmarginleft_inches = 0.0,
		marginleft_inches = 0.45,
		marginright_inches = 0.2,
		margintop_inches = 0.4,
		marginbottom_inches = 0.3,
		cbar_height_inches = 0,
		cbar_width_inches = 0,
		cbar_bottompadding_inches = 0,
		cbar_rightpadding_inches = 0,
		cbar_toppadding_inches = 0,
		cbar_leftpadding_inches = 0,
		cbar_width_percent = None,
		nbr_of_cbars = 1,
		title_height_inches = 0,
		base_fontsize = None,
		add_lettering = False,
		letter_format = '%s',
		#letter_format = '(%s)',
		letter_fontsize = None,
		#letter_fontweight = 'normal',
		letter_fontweight = 'bold',
		letter_offsetx_inches = None, 
		letter_offsety_inches = None,
		letter_offset_number = 0,
		dpi = None,
		**kw
	):

		if dpi is None:
			dpi = DPI
		self.dpi = dpi

		if figw_inches is None:
			figw_inches = TWOCOLUMN_WIDTH_INCHES

		if base_fontsize is None:
			base_fontsize = FONTSIZE
		self.base_fontsize = base_fontsize

		self.add_lettering = add_lettering
		self.letter_format = letter_format
		self.letter_offset_number = letter_offset_number
		if letter_fontsize is None:
			letter_fontsize = base_fontsize
		self.letter_fontsize = letter_fontsize
		self.letter_fontweight = letter_fontweight
		if letter_offsetx_inches is None:
			letter_offsetx_inches = 0.01
		self.letter_offsetx_inches = letter_offsetx_inches
		if letter_offsety_inches is None:
			letter_offsety_inches = 0.02
		self.letter_offsety_inches = letter_offsety_inches

		try:
			show_cbar = kw['show_cbar']
		except:
			show_cbar = True
		if show_cbar:
			total_cbar_width_inches = nbr_of_cbars*(cbar_leftpadding_inches+cbar_rightpadding_inches+cbar_width_inches)
			total_cbar_height_inches = nbr_of_cbars*(cbar_toppadding_inches+cbar_bottompadding_inches+cbar_height_inches)
		else:
			total_cbar_width_inches = 0
			total_cbar_height_inches = 0

		if nx is None:
			if nbr_of_panels is None or nbr_of_panels == 1:
				nx = 1
			else:
				nx = 2
		if ny is None:
			if nbr_of_panels is None or nbr_of_panels == 1:
				ny = 1
			else:
				ny = np.ceil((1.0 * nbr_of_panels)) / nx

		if nbr_of_panels is None:
			nbr_of_panels = nx * ny
		self.nbr_of_panels = nbr_of_panels

		if figw_inches is not None:
			#axw_inches = (figw_inches-figmarginleft_inches) / (1.0 * nx) - marginleft_inches - marginright_inches
			axw_inches = (figw_inches-figmarginleft_inches-total_cbar_width_inches) / (1.0 * nx) - marginleft_inches - marginright_inches
		else:
			if axw_inches is not None:
				figw_inches = nx * (axw_inches + marginleft_inches + marginright_inches) + figmarginleft_inches + total_cbar_width_inches
			if axh_inches is None:
				axh_inches = axw_inches / aspectratio

		if figh_inches is not None:
			if axh_inches is None:
				#axh_inches = figh_inches / (1.0 * ny) - margintop_inches - marginbottom_inches - cbar_bottompadding_inches - cbar_height_inches
				axh_inches = (figh_inches-total_cbar_height_inches-title_height_inches) / (1.0 * ny) - margintop_inches - marginbottom_inches
			if figw_inches is None:
				axw_inches = axh_inches * aspectratio
				figw_inches = nx * (axw_inches + marginleft_inches + marginright_inches) + figmarginleft_inches + total_cbar_width_inches
		else:
			axh_inches = axw_inches / aspectratio
			figh_inches = ny * (axh_inches + margintop_inches + marginbottom_inches) + \
				total_cbar_height_inches + title_height_inches

		aspectratio = axw_inches / axh_inches
		self.figh_inches = figh_inches
		self.figw_inches = figw_inches
		self.axh_inches = axh_inches
		self.axw_inches = axw_inches

		if False:
			print("New SubplotFigure:")
			print(("  nx: %s" %nx))
			print(("  ny: %s" %ny))
			print(("  aspectratio: %s" %aspectratio))
			print(("  figw_inches: %s" %figw_inches))
			print(("  figh_inches: %s" %figh_inches))
			print(("  axw_inches: %s" %axw_inches))
			print(("  axh_inches: %s" %axh_inches))
			print(("  marginleft_inches: %s" %marginleft_inches))
			print(("  marginright_inches: %s" %marginright_inches))
			print(("  margintop_inches: %s" %margintop_inches))
			print(("  marginbottom_inches: %s" %marginbottom_inches))
		  
		self.figmarginleft = figmarginleft_inches / figw_inches
		self.marginleft = marginleft_inches / figw_inches
		self.marginright = marginright_inches / figw_inches
		self.margintop = margintop_inches / figh_inches
		self.marginbottom = marginbottom_inches / figh_inches
		self.title_height = title_height_inches / figh_inches
		self.cbar_width = cbar_width_inches / figw_inches
		self.cbar_height = cbar_height_inches / figh_inches
		self.cbar_rightpadding = cbar_rightpadding_inches / figw_inches
		self.cbar_bottompadding = cbar_bottompadding_inches / figh_inches
		self.cbar_leftpadding = cbar_leftpadding_inches / figw_inches
		self.cbar_toppadding = cbar_toppadding_inches / figh_inches
		self.total_cbar_width = total_cbar_width_inches / figw_inches
		self.total_cbar_height = total_cbar_height_inches / figh_inches
		self.cbar_width_percent = cbar_width_percent
		self.nbr_of_cbars = nbr_of_cbars
		self.cbars_drawn = 0
		self.axw = (1.-self.figmarginleft-self.total_cbar_width)/nx - self.marginleft - self.marginright
		#self.axh = 1./ny - self.margintop - self.marginbottom - self.cbar_bottompadding - self.cbar_height
		self.axh = (1.-self.total_cbar_height-self.title_height)/ny - self.margintop - self.marginbottom
		self.nx = nx
		self.ny = ny
		self.fig = plt.figure(figsize = (figw_inches, figh_inches,), dpi = self.dpi)

	def title(self, text = None, fontsize = None):
		self.fig.suptitle(
			text, 
			fontsize = fontsize,
			verticalalignment = 'center',
			y = 1.-0.5*self.title_height
		)
		# ax = plt.gca()
		# a = self.fig.add_axes((
		# 	0,
		# 	1.-self.title_height,
		# 	1.,
		# 	0,
		# ))
		# plt.axis('off')
		# plt.title(text, fontsize = fontsize)
		# plt.sca(ax)

	def draw_colorbar(self, 
		cmap = None,
		mappable = None,
		fontsize = None,
		ticks = None,
		fmt = None, 
		vmax = None, 
		vmin = None, 
		desc = None,
		number_of_cbar_ticks = None,
		alpha = None,
		extend = None,
		left = None,
		rightmargin = 0,
		top = None
		#center_colorbar = True
	):
		if extend is None:
			extend = 'neither'
		ax = plt.gca()
		if self.cbar_width>0:
			orientation = 'vertical'
			right = self.cbar_rightpadding + self.cbars_drawn*self.total_cbar_width/self.nbr_of_cbars
			left = 1. - right - self.cbar_width
			top = self.margintop
			height = 1.-self.margintop-self.marginbottom
			bottom = 1. - top - height

			if desc is not None:
				dpi = 72.
				#dpi = self.dpi
				# Find width of text:
				bb = matplotlib.textpath.TextPath((0,0),desc,size=fontsize).get_extents()
				bh = bb.height / self.figh_inches / dpi
				air = 4. / self.figh_inches / dpi
				a = self.fig.text(
					#left + self.cbar_width/2.,
					left,
					1. - top + air,
					desc, 
					ha = 'left',
					va = 'bottom',
					fontsize = fontsize
				)
			cax = self.fig.add_axes((
				left,
				bottom,
				self.cbar_width,
				height,
			))
		else:
			orientation = 'horizontal'
			bottom = self.cbar_bottompadding + self.cbars_drawn*self.total_cbar_height/self.nbr_of_cbars
			totalwidth = 1.-self.marginleft-self.marginright
			if self.cbar_width_percent is None:
				#if desc is None:
				self.cbar_width_percent = 100.
				#else:
				#	self.cbar_width_percent = 60.
			shrink = totalwidth * (100.-self.cbar_width_percent) / 100.
			if left is None:
				width = totalwidth - shrink
				left = self.marginleft + shrink*0.5
				#left = self.marginleft + 
				#print(left)
			else:
				width = totalwidth - shrink - left + self.marginleft

			if desc is not None:
				dpi = 72.
				#dpi = self.dpi
				# Find width of text:
				bb = matplotlib.textpath.TextPath((0,0),desc,size=fontsize).get_extents()
				bw = bb.width / self.figw_inches / dpi
				#air = totalwidth*0.02
				air = 4. / self.figw_inches / dpi
				#print(bb.width,bw,left,bw+air*2)
				if 1:
					left = self.marginleft+bw+air*2
					width = totalwidth-bw-air*3-rightmargin
					#if bw>left+air*2:
					#	width += left 
					#	left = bw+air
					#	width -= left 
				else:
					ww = air + bw
					#print(bb.width,width,ww,)
					width -= ww
					left += ww 
				#left = 1. - self.marginright - width - air
				a = self.fig.text(
					#0.5*(left+self.marginleft+air),
					left-air,
					bottom + 0.5*self.cbar_height,
					desc, 
					ha = 'right',
					va = 'center',
					fontsize = fontsize
				)
			if 0:
				if desc is not None:
					air = totalwidth*0.05
					left = 1. - self.marginright - width - air
					a = self.fig.text(
						#0.5*(left+self.marginleft+air),
						left-air/2.,
						bottom + 0.5*self.cbar_height,
						desc, 
						ha = 'right',
						va = 'center',
						fontsize = fontsize
					)
				else:
					left = self.marginleft + shrink*0.5
			cax = self.fig.add_axes((
				left,
				bottom,
				width,
				self.cbar_height,
			))

		if alpha is not None:
			my_cmap = cmap(np.arange(cmap.N))
			# Define the alphas
			alphas = np.linspace(0, 1, cmap.N)
			# Define the background
			BG = np.asarray([1., 1., 1.,])
			# Mix the colors with the background
			for i in range(cmap.N):
				my_cmap[i,:-1] = my_cmap[i,:-1] * alpha + BG * (1.-alpha)
			# Create new colormap
			cmap = ListedColormap(my_cmap)

		cb = ColorbarBase(
			cax, 
			mappable,
			cmap=cmap, 
			orientation=orientation, 
			ticks = ticks, 
			format = fmt,
			norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax),
			extend = extend
		)
		if ticks is None and number_of_cbar_ticks is not None:
			from matplotlib import ticker
			tick_locator = ticker.MaxNLocator(nbins=number_of_cbar_ticks)
			cb.locator = tick_locator
			cb.update_ticks()

		#plt.colorbar(orientation='horizontal',cax=cax, ticks=ticks)
		if fontsize is not None:
			cax.tick_params(labelsize=fontsize-1)
		self.cbars_drawn += 1
		plt.sca(ax)

	def subplot(self, 
		i = 0, 
		letter = None, 
		offsetx_inches = None, 
		offsety_inches = None
	):
		if offsetx_inches is None:
			offsetx_inches = self.letter_offsetx_inches
			#offset_x_inches = self.axw_inches / 25.
		if offsety_inches is None:
			offsety_inches = self.letter_offsety_inches
			#offset_y_inches = self.axh_inches / 25.
		#print 'Width, height:', self.axw_inches, self.axh_inches

		# Special case for last row
		row = np.floor((1.*i)/self.nx) + 1
		addx = 0.
		if row==self.ny and self.nbr_of_panels<self.nx*self.ny:
			addx = (self.nx*self.ny-self.nbr_of_panels)*.5/self.nx

		xpos = addx + (1.-self.figmarginleft)/self.nx * (i%self.nx) + self.marginleft + self.figmarginleft
		boxh = (1.-self.total_cbar_height-self.title_height)/self.ny
		ypos = 1. - boxh * row + self.marginbottom - self.title_height
		#ypos = 1. -  1./self.ny * np.floor(0.5*(i+self.nx)) + self.marginbottom
		#print("%i: xpos = %s, ypos = %s" %(i, xpos, ypos))
		ax = self.fig.add_axes([xpos, ypos, self.axw, self.axh])#, aspect = aspectratio)
		if self.add_lettering:
			if letter is None:
				letter = LETTERS[i+self.letter_offset_number]
			t = self.letter_format %letter
			#print offsetx_inches, offsety_inches
			#print xpos, xpos-self.marginleft+offsetx_inches/self.axw_inches
			#print ypos,offsety_inches,self.axh_inches
			plt.figtext(
				xpos-self.marginleft+offsetx_inches/self.figh_inches,
				ypos+self.axh+self.margintop-offsety_inches/self.figh_inches,
				#ypos+self.axh,
				t,
				fontsize = self.letter_fontsize,
				fontweight = self.letter_fontweight,
				horizontalalignment='left',
				verticalalignment='top'
			)
		return ax

class SubplotFigure(SubplotFigureBase):
	def __init__(self,**kw):
		super().__init__(**kw)
		self.letter_format = '%s'
		#self.letter_format = '(%s)'
		self.letter_fontsize = FONTSIZE+1
		#self.letter_fontweight = 'normal'
		self.letter_fontweight = 'bold'