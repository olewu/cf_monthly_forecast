#!

#--------------------IMPORT NECESSARY PACKAGES-------------------#

# OS interactions and calls:
import os
import subprocess as sbp
import sys
import json

# project specific configurations:
from cf_monthly_forecast.config import *
import cf_monthly_forecast.plot_annotations as pla
import cf_monthly_forecast.plot_options_monthly as pom
import cf_monthly_forecast.vis_config as vc

# data access
import xarray as xr
from netCDF4 import Dataset

# data processing
import numpy as np
from scipy import interpolate
from datetime import datetime
from calendar import monthrange
from cf_monthly_forecast.smooth2d import box_smooth_2D

# plotting
import matplotlib.pyplot as plt
from cf_monthly_forecast.vis_utils import TWOCOLUMN_WIDTH_INCHES,SubplotFigure
from mpl_toolkits.basemap import Basemap

# function to send email
from cf_monthly_forecast.utils import send_email

# direct print output to log file:
logfile_path = '{0:s}/logs/fc_monthly_anom_plt.log'.format(proj_base)
sys.stdout = open(logfile_path, 'a')


#--------------------SOME INPUT--------------------#

# fontsize:
FS = 9.
# figure width:
figw_inches = TWOCOLUMN_WIDTH_INCHES*.8

# splines used for interpolation
nsplines = 4

# 'model' key word for looking plotting parameters and units:
model = 'ens_mean_anom'

#--------------------CHECK FOR EXISTENCE OF FORECAST FILE--------------------#

# get current date during time of running the script:
today = datetime.today()
# today = datetime(2022,11,15)
initmonth = today.month
inityear = today.year

# check for existence of production files of single parameters:

plt_vars = []

for pvar in pom.variables:
    fname = '{0:s}/{3:s}/forecast_production_{3:s}_{1:d}_{2:d}.nc'.format(
        dirs['SFE_monthly'],
        inityear,
        initmonth,
        file_key[pvar]
    )

    if os.path.isfile(fname):
        plt_vars.append(pvar)

if len(plt_vars) == 0:
    print('{0:} (UTC)\tNo monthly forecast files exist yet for initialization {1:d}-{2:d}!\n'.format(datetime.now(),inityear,initmonth))
    sys.exit()
else:
    print('{0:} (UTC)\tMonthly forecast files exist for initialization {1:d}-{2:d}, creating anomaly plots for {3:}.\n'.format(datetime.now(),inityear,initmonth,plt_vars))

missing_vars = [pv for pv in pom.variables if pv not in plt_vars]

# check if the script has already run but was missing files:
idx_file_missing = '{0:s}/data/index/missing_anom_{1:d}-{2:s}.ix'.format(proj_base,inityear,str(initmonth).zfill(2))
if os.path.isfile(idx_file_missing):
    with open(idx_file_missing,'r') as ix_miss_file:
        mlist = ix_miss_file.readlines()
    mlist = [lel[:-1] for lel in list(set(mlist))]

    # update plt_vars to only go through the missing variables:
    plt_vars = [v for v in plt_vars if v in mlist]

#--------------------MAKE A DIRECTORY FOR THE FIGURES--------------------#

# define where forecasts are located and where figures should be saved:
figdir = '{0:s}/monthly_fc/init_{1:s}-{2:s}/anomalies/'.format(
    dirs['public'],str(inityear).zfill(4),str(initmonth).zfill(2)
)

#--------------------CHECK IF JSON FILE WITH THE PARTICIPATING SYSTEMS EXISTS--------------------#
# try loading the json file that contains info on the systems participating in the MME:
ps_filename = os.path.join('{0:s}'.format(dirs['processed']),'systems_{0:d}-{1:0>2d}.json'.format(inityear,initmonth))
if os.path.isfile(ps_filename):
    with open(ps_filename, 'r') as f:
        participating_systems = json.load(f)
else:
    # if it doesn't find the json file it will assume all systems are there
    participating_systems = [sys for _,sys in dt_systems_lookups.items()]

# send email in case the script fails for some reason (error message will be in log file)!
try:
    # create a folder for the initialization if it doesn't already exist:
    if not os.path.exists(figdir):
        os.makedirs(figdir,exist_ok=False) # creates directories recursively!


    for variable in plt_vars:

        #--------------------LOAD FORECAST DATA FOR REQUESTED VARIABLE--------------------#
        varf_name = file_key[variable]
        FILE = '{0:s}/{3:s}/forecast_production_{3:s}_{1:d}_{2:d}.nc'.format(dirs['SFE_monthly'],inityear,initmonth,varf_name)
        
        ds = xr.open_dataset(FILE)

        # get grid info as arrays for plotting and interpolation:
        LON,LAT = np.meshgrid(ds.lon,ds.lat)

        #--------------------FORECAST MONTHS TO LOOP OVER--------------------#
        # loop over forecast months & note that index 0 is forecast month 1!! (e.g. May init, index 0 has June monthly mean)
        FCMONTHS = np.array(ds.variables['target_month'][:],dtype=int)
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

        for fcmonth,fcyear in zip(FCMONTH,FCYEAR):
            
            for area in pom.DOMAINS:
                # weights:
                glat0 = 40
                glat1 = 70
                gpoints = np.nonzero((LAT.ravel()>=glat0)&(LAT.ravel()<=glat1))[0]
                gweights = np.cos(np.radians(LAT.ravel()[gpoints]))
                gweights /= np.sum(gweights)
                points = np.nonzero(
                    (LON.ravel() >= vc.area_specs[area]['lon0']) &
                    (LON.ravel() <= vc.area_specs[area]['lon1']) &
                    (LAT.ravel() >= vc.area_specs[area]['lat0']) &
                    (LAT.ravel() <= vc.area_specs[area]['lat1'])
                )[0]
                weights = np.cos(np.radians(LAT.ravel()[points]))
                weights /= np.sum(weights)

                if nsplines:
                    lon2 = np.linspace(LON[0,0],LON[0,-1],LON.shape[1]*nsplines)
                    lat2 = np.linspace(LAT[0,0],LAT[-1,0],LAT.shape[0]*nsplines)
                    lon3,lat3 = np.meshgrid(lon2,lat2)
                    xi,yi = vc.area_specs[area]['bm'](lon3,lat3)
                else:
                    xi,yi = vc.area_specs[area]['bm'](LON,LAT)
                    xp,yp = vc.area_specs[area]['bm'](LON-.25,LAT-.25)
            
                if model == 'ens_mean_anom':
                    if variable == 'pr':
                        a = (ds.mean_standardized_anomaly * ds.sd_era).sel(target_month=fcmonth).values * units_tf_factor[variable] * monthrange(fcyear,fcmonth)[1]
                    else:
                        a = (ds.mean_standardized_anomaly * ds.sd_era).sel(target_month=fcmonth).values * units_tf_factor[variable]
                # Smooth the anomaly fields:
                a_sm9 = box_smooth_2D(a,1,1,latitude=LAT[:,0])
                a_sm25 = box_smooth_2D(a,2,2,latitude=LAT[:,0])
                
                try:
                    cv = pom.cvs[model][variable][area]
                except:
                    try:
                        cv = pom.cvs[model][variable]
                    except:
                        cv = pom.cvs[model]
                ticks = cv
                fmt = pom.FMT[variable]
                try:
                    cmapname = pom.cmapnames[model][variable]
                except:
                    cmapname = pom.cmapnames[model]
                cmap = plt.get_cmap(cmapname,len(cv)-1)

                # Compute area average:
                gavg = np.sum(a.ravel()[gpoints]*gweights)
                avg = np.sum(a.ravel()[points]*weights)
                print(model,avg)
                
                print(variable,np.min(a),np.max(a))
                for lang in pom.langs:
                    mstr = pla.monthnames[lang][fcmonth-1]
                    title = ''
                    if model in ('ens_mean_anom',):
                        title = {
                            'en': '{2:s} Ensemble Mean Anomaly {0:s} {1:d}'.format(
                                mstr,
                                fcyear,
                                long_names[variable]['en']
                            ),
                            'no': '{2:s} gjennomsnittige anomali {0:s} {1:d}'.format(
                                mstr,
                                fcyear,
                                long_names[variable]['no']
                            )
                        }[lang]

                    # Initialize Figure
                    fig = SubplotFigure(
                        figw_inches = figw_inches,
                        aspectratio = vc.area_specs[area]['aspectratio'],
                        marginleft_inches = 0.05,
                        marginright_inches = 0.05,
                        margintop_inches = 0.45,
                        marginbottom_inches = 0.05,
                        cbar_height_inches = .15,
                        cbar_bottompadding_inches = .25,
                        cbar_toppadding_inches = .05,
                        cbar_width_percent = 95.
                    )
                    ax = fig.subplot(0)
                    if nsplines:
                        print('linearly interpolating data to {0:d}x the resolution'.format(nsplines))
                        f = interpolate.interp2d(LON[0,:], LAT[:,0], a, kind='linear')
                        a = f(lon2,lat2)
                    spr = cv[-1]-cv[0]
                    a[a<=cv[0]] = cv[0]+spr/1000.
                    a[a>=cv[-1]] = cv[-1]-spr/1000.
                    levels = np.arange(cv[0],cv[-1])
                    hatches = [None]*(len(cv)-1)
                    # Plot probabilities:
                    cf = ax.contourf(xi,yi,a,cv,cmap=cmap,vmin=cv[0],vmax=cv[-1],hatches=hatches,extend='both')
                    vc.area_specs[area]['bm'].drawcoastlines(linewidth=.5)
                    vc.area_specs[area]['bm'].drawcountries(linewidth=.35,color='.5')
                    if not area in ('GLOBAL',):
                        tkw = {
                            'horizontalalignment':'left',
                            'verticalalignment':'top',
                            'transform':ax.transAxes
                        }
                        t1 = '%s'%{'no':'Varsel fra','en':'Forecast from'}[lang]
                        t1 += ' Climate Futures'
                        plt.text(0.01,.99,t1,fontweight='bold',fontsize=FS-2,**tkw)
                        t = {'no':'Finansiert av Forskningsrådet','en':'Funded by the Research Council of Norway'}[lang]
                        t += '\n%s:'%{'no':'Basert på data fra','en':'Based on data from'}[lang]
                        if 'ecmwf' in participating_systems:
                            t += '\nECMWF (%s)'%{'no':'Europa','en':'Europe'}[lang]
                        if 'ukmo' in participating_systems:
                            t += '\nUK Met Office (%s)'%{'no':'Storbritannia','en':'UK'}[lang]
                        if 'cmcc' in participating_systems:	
                            t += '\nCMCC (%s)'%{'no':'Italia','en':'Italy'}[lang]
                        if 'meteo_france' in participating_systems:	
                            t += '\nMétéo France (%s)'%{'no':'Frankrike','en':'France'}[lang]
                        if 'dwd' in participating_systems:	
                            t += '\nDWD (%s)'%{'no':'Tyskland','en':'Germany'}[lang]
                        if 'bccr' in participating_systems:	
                            t += '\nBjerknes Centre (%s)'%{'no':'Norge','en':'Norway'}[lang]
                        t += '\n{0:s} {1:d} {2:s} {3:d}'.format({'no':'Utarbeidet','en':'Produced'}[lang],today.day,pla.monthnames[lang][today.month-1],today.year)
                        plt.text(0.01,.94,t,fontsize=FS-4,**tkw)
                    plt.title(title,fontsize = FS-1)
                    desc = dict(
                        en = 'Anomaly ({0:s})'.format(units_plot[variable]),
                        no = 'Anomali ({0:s})'.format(units_plot[variable])
                        )[lang]
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
                        fmt = fmt,
                        extend='both'
                    )
                    filename = 'fc_{0:s}_{1:s}_{2:s}_{3:s}_{4:s}'.format(
                        variable,
                        str(fcmonth).zfill(2),
                        model,
                        area,
                        lang
                    )
                    
                    # print(filename)

                    # fig.fig.savefig('{0:s}{1:s}.png'.format(figdir,filename),dpi=300)
                    plt.close(fig.fig)

                    #------------------PLOT SMOOTHED FIELD------------------#
                    # Initialize Figure
                    fig_sm1 = SubplotFigure(
                        figw_inches = figw_inches,
                        aspectratio = vc.area_specs[area]['aspectratio'],
                        marginleft_inches = 0.05,
                        marginright_inches = 0.05,
                        margintop_inches = 0.45,
                        marginbottom_inches = 0.05,
                        cbar_height_inches = .15,
                        cbar_bottompadding_inches = .25,
                        cbar_toppadding_inches = .05,
                        cbar_width_percent = 95.
                    )
                    ax_sm1 = fig_sm1.subplot(0)
                    if nsplines:
                        print('linearly interpolating data to {0:d}x the resolution'.format(nsplines))
                        f1 = interpolate.interp2d(LON[0,:], LAT[:,0], a_sm9, kind='linear')
                        a_sm9 = f1(lon2,lat2)
                    spr = cv[-1]-cv[0]
                    a_sm9[a_sm9<=cv[0]] = cv[0]+spr/1000.
                    a_sm9[a_sm9>=cv[-1]] = cv[-1]-spr/1000.
                    # Plot probabilities:
                    cf_sm1 = ax_sm1.contourf(xi,yi,a_sm9,cv,cmap=cmap,vmin=cv[0],vmax=cv[-1],hatches=hatches,extend='both')
                    vc.area_specs[area]['bm'].drawcoastlines(linewidth=.5)
                    vc.area_specs[area]['bm'].drawcountries(linewidth=.35,color='.5')
                    if not area in ('GLOBAL',):
                        tkw = {
                            'horizontalalignment':'left',
                            'verticalalignment':'top',
                            'transform':ax_sm1.transAxes
                        }
                        plt.text(0.01,.99,t1,fontweight='bold',fontsize=FS-2,**tkw)
                        plt.text(0.01,.94,t,fontsize=FS-4,**tkw)
                    plt.title(title,fontsize = FS-1)

                    fig_sm1.draw_colorbar(
                        mappable = cf_sm1,
                        fontsize=FS-1, 
                        cmap = cmap, 
                        vmin = cv[0], 
                        vmax = cv[-1],
                        desc = desc,
                        ticks = ticks,
                        rightmargin = rightmargin,
                        fmt = fmt,
                        extend='both'
                    )
                    filename_sm1 = 'fc_{0:s}_{1:s}_{2:s}_{3:s}_{4:s}_9gpkernel'.format(
                        variable,
                        str(fcmonth).zfill(2),
                        model,
                        area,
                        lang
                    )
                    
                    print(filename_sm1)

                    fig_sm1.fig.savefig('{0:s}{1:s}.png'.format(figdir,filename_sm1),dpi=300)
                    plt.close(fig_sm1.fig)
                    
                    # 
                    fig_sm2 = SubplotFigure(
                        figw_inches = figw_inches,
                        aspectratio = vc.area_specs[area]['aspectratio'],
                        marginleft_inches = 0.05,
                        marginright_inches = 0.05,
                        margintop_inches = 0.45,
                        marginbottom_inches = 0.05,
                        cbar_height_inches = .15,
                        cbar_bottompadding_inches = .25,
                        cbar_toppadding_inches = .05,
                        cbar_width_percent = 95.
                    )
                    ax_sm2 = fig_sm2.subplot(0)
                    if nsplines:
                        print('linearly interpolating data to {0:d}x the resolution'.format(nsplines))
                        f2 = interpolate.interp2d(LON[0,:], LAT[:,0], a_sm25, kind='linear')
                        a_sm25 = f2(lon2,lat2)
                    spr = cv[-1]-cv[0]
                    a_sm25[a_sm25<=cv[0]] = cv[0]+spr/1000.
                    a_sm25[a_sm25>=cv[-1]] = cv[-1]-spr/1000.
                    # Plot probabilities:
                    cf_sm2 = ax_sm2.contourf(xi,yi,a_sm25,cv,cmap=cmap,vmin=cv[0],vmax=cv[-1],hatches=hatches,extend='both')
                    vc.area_specs[area]['bm'].drawcoastlines(linewidth=.5)
                    vc.area_specs[area]['bm'].drawcountries(linewidth=.35,color='.5')
                    if not area in ('GLOBAL',):
                        tkw = {
                            'horizontalalignment':'left',
                            'verticalalignment':'top',
                            'transform':ax_sm2.transAxes
                        }
                        plt.text(0.01,.99,t1,fontweight='bold',fontsize=FS-2,**tkw)
                        plt.text(0.01,.94,t,fontsize=FS-4,**tkw)
                    plt.title(title,fontsize = FS-1)

                    fig_sm1.draw_colorbar(
                        mappable = cf_sm2,
                        fontsize=FS-1, 
                        cmap = cmap, 
                        vmin = cv[0], 
                        vmax = cv[-1],
                        desc = desc,
                        ticks = ticks,
                        rightmargin = rightmargin,
                        fmt = fmt,
                        extend='both'
                    )
                    filename_sm2 = 'fc_{0:s}_{1:s}_{2:s}_{3:s}_{4:s}_25gpkernel'.format(
                        variable,
                        str(fcmonth).zfill(2),
                        model,
                        area,
                        lang
                    )
                    
                    # print(filename_sm2)

                    # fig_sm2.fig.savefig('{0:s}{1:s}.png'.format(figdir,filename_sm2),dpi=300)
                    plt.close(fig_sm2.fig)

        
        if variable == 'pr':
            print('relative anomalies')

            for fcmonth,fcyear in zip(FCMONTH,FCYEAR):

                for area in pom.DOMAINS:
                    # weights:
                    glat0 = 40
                    glat1 = 70
                    gpoints = np.nonzero((LAT.ravel()>=glat0)&(LAT.ravel()<=glat1))[0]
                    gweights = np.cos(np.radians(LAT.ravel()[gpoints]))
                    gweights /= np.sum(gweights)
                    points = np.nonzero(
                        (LON.ravel() >= vc.area_specs[area]['lon0']) &
                        (LON.ravel() <= vc.area_specs[area]['lon1']) &
                        (LAT.ravel() >= vc.area_specs[area]['lat0']) &
                        (LAT.ravel() <= vc.area_specs[area]['lat1'])
                    )[0]
                    weights = np.cos(np.radians(LAT.ravel()[points]))
                    weights /= np.sum(weights)

                    if nsplines:
                        lon2 = np.linspace(LON[0,0],LON[0,-1],LON.shape[1]*nsplines)
                        lat2 = np.linspace(LAT[0,0],LAT[-1,0],LAT.shape[0]*nsplines)
                        lon3,lat3 = np.meshgrid(lon2,lat2)
                        xi,yi = vc.area_specs[area]['bm'](lon3,lat3)
                    else:
                        xi,yi = vc.area_specs[area]['bm'](LON,LAT)
                        xp,yp = vc.area_specs[area]['bm'](LON-.25,LAT-.25)
                
                    if model == 'ens_mean_anom':
                        a = (ds.mean_standardized_anomaly * ds.sd_era / ds.climatology_era).sel(target_month=fcmonth).values * 100
                    # smooth the relative anomalies:
                    a_sm9 = box_smooth_2D(a,1,1,latitude=LAT[:,0])
                    a_sm25 = box_smooth_2D(a,2,2,latitude=LAT[:,0])

                    if area == 'EUROPE':
                        cv = np.linspace(-50,50,11)
                    elif area == 'GLOBAL':
                        cv = np.linspace(-100,100,11)
                    ticks = cv
                    fmt = pom.FMT[variable]
                    try:
                        cmapname = pom.cmapnames[model][variable]
                    except:
                        cmapname = pom.cmapnames[model]
                    cmap = plt.get_cmap(cmapname,len(cv)-1)

                    # Compute area average:
                    gavg = np.sum(a.ravel()[gpoints]*gweights)
                    avg = np.sum(a.ravel()[points]*weights)
                    print(model,avg)
                    
                    print(variable,np.min(a),np.max(a))
                    for lang in pom.langs:
                        mstr = pla.monthnames[lang][fcmonth-1]
                        title = ''
                        if model in ('ens_mean_anom',):
                            title = {
                                'en': '{2:s} Ensemble Mean Percent Deviation from Climatology {0:s} {1:d}'.format(
                                    mstr,
                                    fcyear,
                                    long_names[variable]['en']
                                ),
                                'no': '{2:s} gjennomsnittige anomali {0:s} {1:d}'.format(
                                    mstr,
                                    fcyear,
                                    long_names[variable]['no']
                                )
                            }[lang]

                        fig = SubplotFigure(
                            figw_inches = figw_inches,
                            aspectratio = vc.area_specs[area]['aspectratio'],
                            marginleft_inches = 0.05,
                            marginright_inches = 0.05,
                            margintop_inches = 0.45,
                            marginbottom_inches = 0.05,
                            cbar_height_inches = .15,
                            cbar_bottompadding_inches = .25,
                            cbar_toppadding_inches = .05,
                            cbar_width_percent = 95.
                        )
                        ax = fig.subplot(0)
                        if nsplines:
                            print('linearly interpolating data to {0:d}x the resolution'.format(nsplines))
                            if np.isinf(a).sum() > 0:
                                print('Some points are inf!')
                            a[np.isinf(a)] = np.sign(a[np.isinf(a)]) * 999
                            f = interpolate.interp2d(LON[0,:], LAT[:,0], a, kind='linear')
                            a = f(lon2,lat2)
                        spr = cv[-1]-cv[0]
                        a[a<=cv[0]] = cv[0]+spr/1000.
                        a[a>=cv[-1]] = cv[-1]-spr/1000.
                        levels = np.arange(cv[0],cv[-1])
                        hatches = [None]*(len(cv)-1)
                        # Plot probabilities:
                        cf = ax.contourf(xi,yi,a,cv,cmap=cmap,vmin=cv[0],vmax=cv[-1],hatches=hatches,extend='both')
                        vc.area_specs[area]['bm'].drawcoastlines(linewidth=.5)
                        vc.area_specs[area]['bm'].drawcountries(linewidth=.35,color='.5')
                        if not area in ('GLOBAL',):
                            tkw = {
                                'horizontalalignment':'left',
                                'verticalalignment':'top',
                                'transform':ax.transAxes
                            }
                            t1 = '%s'%{'no':'Varsel fra','en':'Forecast from'}[lang]
                            t1 += ' Climate Futures'
                            plt.text(0.01,.99,t1,fontweight='bold',fontsize=FS-2,**tkw)
                            t = {'no':'Finansiert av Forskningsrådet','en':'Funded by the Research Council of Norway'}[lang]
                            t += '\n%s:'%{'no':'Basert på data fra','en':'Based on data from'}[lang]
                            if 'ecmwf' in participating_systems:
                                t += '\nECMWF (%s)'%{'no':'Europa','en':'Europe'}[lang]
                            if 'ukmo' in participating_systems:
                                t += '\nUK Met Office (%s)'%{'no':'Storbritannia','en':'UK'}[lang]
                            if 'cmcc' in participating_systems:	
                                t += '\nCMCC (%s)'%{'no':'Italia','en':'Italy'}[lang]
                            if 'meteo_france' in participating_systems:	
                                t += '\nMétéo France (%s)'%{'no':'Frankrike','en':'France'}[lang]
                            if 'dwd' in participating_systems:	
                                t += '\nDWD (%s)'%{'no':'Tyskland','en':'Germany'}[lang]
                            if 'bccr' in participating_systems:	
                                t += '\nBjerknes Centre (%s)'%{'no':'Norge','en':'Norway'}[lang]
                            t += '\n{0:s} {1:d} {2:s} {3:d}'.format({'no':'Utarbeidet','en':'Produced'}[lang],today.day,pla.monthnames[lang][today.month-1],today.year)
                            plt.text(0.01,.94,t,fontsize=FS-4,**tkw)
                        plt.title(title,fontsize = FS-1)
                        desc = dict(
                            en = 'Anomaly (%)',
                            no = 'Anomali (%)'
                            )[lang]
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
                            fmt = fmt,
                            extend='both'
                        )
                        filename = 'fc_{0:s}_{1:s}_rel_{2:s}_{3:s}_{4:s}'.format(
                            variable,
                            str(fcmonth).zfill(2),
                            model,
                            area,
                            lang
                        )
                        
                        # print(filename)

                        # fig.fig.savefig('{0:s}{1:s}.png'.format(figdir,filename),dpi=300)
                        plt.close(fig.fig)

                        #------------SMOOTHED FIELDS-----------#
                        fig_sm1 = SubplotFigure(
                            figw_inches = figw_inches,
                            aspectratio = vc.area_specs[area]['aspectratio'],
                            marginleft_inches = 0.05,
                            marginright_inches = 0.05,
                            margintop_inches = 0.45,
                            marginbottom_inches = 0.05,
                            cbar_height_inches = .15,
                            cbar_bottompadding_inches = .25,
                            cbar_toppadding_inches = .05,
                            cbar_width_percent = 95.
                        )
                        ax_sm1 = fig_sm1.subplot(0)
                        if nsplines:
                            print('linearly interpolating data to {0:d}x the resolution'.format(nsplines))
                            if np.isinf(a_sm9).sum() > 0:
                                print('Some points are inf!')
                            a_sm9[np.isinf(a_sm9)] = np.sign(a_sm9[np.isinf(a_sm9)]) * 999
                            f1 = interpolate.interp2d(LON[0,:], LAT[:,0], a_sm9, kind='linear')
                            a_sm9 = f1(lon2,lat2)
                        spr = cv[-1]-cv[0]
                        a_sm9[a_sm9<=cv[0]] = cv[0]+spr/1000.
                        a_sm9[a_sm9>=cv[-1]] = cv[-1]-spr/1000.
                        # Plot probabilities:
                        cf_sm1 = ax_sm1.contourf(xi,yi,a_sm9,cv,cmap=cmap,vmin=cv[0],vmax=cv[-1],hatches=hatches,extend='both')
                        vc.area_specs[area]['bm'].drawcoastlines(linewidth=.5)
                        vc.area_specs[area]['bm'].drawcountries(linewidth=.35,color='.5')
                        if not area in ('GLOBAL',):
                            tkw = {
                                'horizontalalignment':'left',
                                'verticalalignment':'top',
                                'transform':ax_sm1.transAxes
                            }
                            plt.text(0.01,.99,t1,fontweight='bold',fontsize=FS-2,**tkw)
                            plt.text(0.01,.94,t,fontsize=FS-4,**tkw)
                        plt.title(title,fontsize = FS-1)
                        fig_sm1.draw_colorbar(
                            mappable = cf_sm1,
                            fontsize=FS-1, 
                            cmap = cmap, 
                            vmin = cv[0], 
                            vmax = cv[-1],
                            desc = desc,
                            ticks = ticks,
                            rightmargin = rightmargin,
                            fmt = fmt,
                            extend='both'
                        )
                        filename_sm1 = 'fc_{0:s}_{1:s}_rel_{2:s}_{3:s}_{4:s}_9gpkernel'.format(
                            variable,
                            str(fcmonth).zfill(2),
                            model,
                            area,
                            lang
                        )
                        
                        print(filename_sm1)

                        fig_sm1.fig.savefig('{0:s}{1:s}.png'.format(figdir,filename_sm1),dpi=300)
                        plt.close(fig_sm1.fig)

                        fig_sm2 = SubplotFigure(
                            figw_inches = figw_inches,
                            aspectratio = vc.area_specs[area]['aspectratio'],
                            marginleft_inches = 0.05,
                            marginright_inches = 0.05,
                            margintop_inches = 0.45,
                            marginbottom_inches = 0.05,
                            cbar_height_inches = .15,
                            cbar_bottompadding_inches = .25,
                            cbar_toppadding_inches = .05,
                            cbar_width_percent = 95.
                        )
                        ax_sm2 = fig_sm2.subplot(0)
                        if nsplines:
                            print('linearly interpolating data to {0:d}x the resolution'.format(nsplines))
                            if np.isinf(a_sm25).sum() > 0:
                                print('Some points are inf!')
                            a_sm25[np.isinf(a_sm25)] = np.sign(a_sm25[np.isinf(a_sm25)]) * 999
                            f2 = interpolate.interp2d(LON[0,:], LAT[:,0], a_sm25, kind='linear')
                            a_sm25 = f2(lon2,lat2)
                        spr = cv[-1]-cv[0]
                        a_sm25[a_sm25<=cv[0]] = cv[0]+spr/1000.
                        a_sm25[a_sm25>=cv[-1]] = cv[-1]-spr/1000.
                        # Plot probabilities:
                        cf_sm2 = ax_sm2.contourf(xi,yi,a_sm25,cv,cmap=cmap,vmin=cv[0],vmax=cv[-1],hatches=hatches,extend='both')
                        vc.area_specs[area]['bm'].drawcoastlines(linewidth=.5)
                        vc.area_specs[area]['bm'].drawcountries(linewidth=.35,color='.5')
                        if not area in ('GLOBAL',):
                            tkw = {
                                'horizontalalignment':'left',
                                'verticalalignment':'top',
                                'transform':ax_sm2.transAxes
                            }
                            plt.text(0.01,.99,t1,fontweight='bold',fontsize=FS-2,**tkw)
                            plt.text(0.01,.94,t,fontsize=FS-4,**tkw)
                        plt.title(title,fontsize = FS-1)
                        fig_sm2.draw_colorbar(
                            mappable = cf_sm2,
                            fontsize=FS-1, 
                            cmap = cmap, 
                            vmin = cv[0], 
                            vmax = cv[-1],
                            desc = desc,
                            ticks = ticks,
                            rightmargin = rightmargin,
                            fmt = fmt,
                            extend='both'
                        )
                        filename_sm2 = 'fc_{0:s}_{1:s}_rel_{2:s}_{3:s}_{4:s}_25gpkernel'.format(
                            variable,
                            str(fcmonth).zfill(2),
                            model,
                            area,
                            lang
                        )
                        
                        # print(filename_sm2)

                        # fig_sm2.fig.savefig('{0:s}smoothed/{1:s}.png'.format(figdir,filename_sm2),dpi=300)
                        plt.close(fig_sm2.fig)
        
    # write an index file if the script executes as expected:
    # only if no files are missing!
    # if this file exists, the automation will not execute this script
    idx_file = '{0:s}/data/index/complete_anom_{1:d}-{2:s}.ix'.format(proj_base,inityear,str(initmonth).zfill(2))
    if not missing_vars:
        if not os.path.isfile(idx_file):
            sbp.call(
                'touch {0:s}'.format(idx_file),
                shell=True
            )
        subj = 'Successful: Monthly forecast anomaly plot production done {:}'.format(datetime.now())
        send_email(subj,subj)
        # delete the file indicating missing variable(s)
        if os.path.isfile(idx_file_missing):
            sbp.call('rm {0:s}'.format(idx_file_missing),shell=True)
    else: # if not, write a different index file that contains the missing elements
        with open(idx_file_missing,'w') as ix_miss_file:
            for mv in missing_vars:
                ix_miss_file.write('{0:s}\n'.format(mv))

except:
    # send email
    subj = 'Failed: Monthly forecast anomaly plot production failed {:}'.format(datetime.now())
    text = 'Check {0:s} for detailed error message.'.format(logfile_path)
    send_email(subj,text)

