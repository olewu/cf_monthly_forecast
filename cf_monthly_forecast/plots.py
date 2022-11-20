# move plotting functions from 002_forecast_plots.py and 004_forecast_anomalies.py here to make those more readable

from pyparsing import col
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from cf_monthly_forecast.config import *

def derive_abs_limits(x_da,y_da,x_center=None,y_center=None,x_sd=None,y_sd=None):
    """
    """
    
    if x_center is None:
        x_center = x_da.climatology.values
    if y_center is None:
        y_center = y_da.climatology.values

    if x_sd is None:
        x_sd = x_da.sd.values
    if y_sd is None:
        y_sd = y_da.sd.values

    return [x_center-3.5*x_sd,x_center+3.5*x_sd,y_center-3.5*y_sd,y_center+3.5*y_sd]

def bivariate_fc_plot(
        x_ensemble,
        y_ensemble,
        x_clim_mean,
        y_clim_mean,
        fc_probs,
        clim_x = None,
        clim_y = None,
        clim_probs = None,
        plt_lims = None,
        save_path = None,
        fig_name = None,
        x_var_name = 'X',
        y_var_name = 'Y',
        x_pred = None,
        y_pred = None,
        x_units = None, # if None, will be derived from config
        y_units = None, # if None, will be derived from config
        x_fac = None, # if None, will be derived from config, set to 1 to force no scaling
        y_fac = None, # if None, will be derived from config, set to 1 to force no scaling
        title = '',
        print_n = True
    ):
    """
    plt_lims [x_low,x_upp,y_low,y_upp]
    """

    # derive scaling if not specified:
    x_key = [fk for fk,na in file_key.items() if na == x_var_name][0]
    y_key = [fk for fk,na in file_key.items() if na == y_var_name][0]
    x_offs,y_offs = 0,0
    if x_fac is None:
        x_fac = units_tf_factor[x_key]
        if ('temperature' in x_var_name) and (x_ensemble.mean() > 200):
            x_offs = - 273.15
    x_ensemble = x_ensemble * x_fac + x_offs
    x_clim_mean = x_clim_mean * x_fac + x_offs
    if y_fac is None:
        y_fac = units_tf_factor[y_key]
        if ('temperature' in y_var_name) and (y_ensemble.mean() > 200):
            y_offs = - 273.15
    y_ensemble = y_ensemble * y_fac + y_offs
    y_clim_mean = y_clim_mean * y_fac + y_offs

    # Units:
    if x_units is None:
        x_units = units_plot[x_key]
    if y_units is None:
        y_units = units_plot[y_key]

    x_em = x_ensemble.mean(); y_em = y_ensemble.mean()

    f,ax = plt.subplots(figsize=(7,7))
    
    if 'precipitation' in x_var_name and plt_lims is not None:
        plt_lims[0] = -.0001
        x_ensemble[x_ensemble < 0] = 0
    if 'precipitation' in y_var_name and plt_lims is not None:
        plt_lims[2] = -.0001
        y_ensemble[y_ensemble < 0] = 0
    
    ax.scatter(x_ensemble,y_ensemble,c='C0',marker='o',s=25,clip_on=True) #,color='none',edgecolor='C0'
    
    if clim_x is not None and clim_y is not None:
        #create scatterplot
        # ax.scatter(clim_x.values,clim_y.values,c='none',marker='.',zorder=10)
        ax.scatter(clim_x.values,clim_y.values,c='none',edgecolor='k',marker='o',zorder=10)

        #use for loop to add annotations to each point in plot 
        # for i, clim_t in enumerate(clim_x.time):
        #     txt = str(clim_t.dt.year.item())[2:]
        #     ax.annotate(txt, (clim_x[i], clim_y[i]),fontsize=9,color='k',zorder=10,ha='center',va='center')
        
    if plt_lims is None:
        xlims = ax.get_xlim(); ylims = ax.get_ylim()
        if 'precipitation' in x_var_name:
            ax.set_xlim([-.01,xlims[-1]])
        if 'precipitation' in y_var_name:
            ax.set_ylim([-.01,ylims[-1]])
    else:
        xlims = [pl*x_fac+x_offs for pl in plt_lims[:2]]
        ylims = [pl*y_fac+y_offs for pl in plt_lims[2:]]

    ax.set_xlim(xlims)
    ax.set_ylim(ylims)

    ax.vlines(x_clim_mean,ylims[0],ylims[1],color='k',ls='solid',lw=2,label='obs')
    ax.hlines(y_clim_mean,xlims[0],xlims[1],color='k',ls='solid',lw=2)
    ax.vlines(x_em,ylims[0],ylims[1],color='C0',lw=2,label='forecast')
    ax.hlines(y_em,xlims[0],xlims[1],color='C0',lw=2)

    if x_pred is not None:
        ax.vlines(x_pred,ylims[0],ylims[1],color='C1',alpha=.5,ls='solid',lw=2,label='trend')
    if y_pred is not None:
        ax.hlines(y_pred,xlims[0],xlims[1],color='C1',alpha=.5,ls='solid',lw=2)
    print(x_clim_mean,x_em.values,y_clim_mean,y_em.values)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                    box.width, box.height * 0.9])

    # Put a legend below current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.11),
            fancybox=True, shadow=True, ncol=3,fontsize=14)

    # annotate:
    props = dict(boxstyle='round', facecolor='w', alpha=0.5,lw=2)
    e = ['k','k','k','k']
    max_prob_arg = np.array(fc_probs).argmax()
    # highlight box with highest chance of occurrence:
    e[max_prob_arg] = 'r'

    if clim_probs is None:
        ax.text(.975,.975,'wet & warm:\n{0:2.1f}%'.format(fc_probs[0]),va='top',ha='right',fontsize=15,transform=ax.transAxes, bbox = dict(props.items(),edgecolor=e[0]),zorder=11)
        ax.text(.975,.025,'dry & warm:\n{0:2.1f}%'.format(fc_probs[1]),va='bottom',ha='right',fontsize=15,transform=ax.transAxes, bbox = dict(props.items(),edgecolor=e[1]),zorder=11)
        ax.text(0.025,.025,'dry & cold:\n{0:2.1f}%'.format(fc_probs[2]),va='bottom',ha='left',fontsize=15,transform=ax.transAxes, bbox = dict(props.items(),edgecolor=e[2]),zorder=11)
        ax.text(0.025,.975,'wet & cold:\n{0:2.1f}%'.format(fc_probs[3]),va='top',ha='left',fontsize=15,transform=ax.transAxes, bbox = dict(props.items(),edgecolor=e[3]),zorder=11)
    else:
        ax.text(.975,.975,'wet & warm:\n{0:2.1f}% ({1:2.1f}%)'.format(fc_probs[0],clim_probs[0]),va='top',ha='right',fontsize=15,transform=ax.transAxes, bbox = dict(props.items(),edgecolor=e[0]),zorder=11)
        ax.text(.975,.025,'dry & warm:\n{0:2.1f}% ({1:2.1f}%)'.format(fc_probs[1],clim_probs[1]),va='bottom',ha='right',fontsize=15,transform=ax.transAxes, bbox = dict(props.items(),edgecolor=e[1]),zorder=11)
        ax.text(0.025,.025,'dry & cold:\n{0:2.1f}% ({1:2.1f}%)'.format(fc_probs[2],clim_probs[2]),va='bottom',ha='left',fontsize=15,transform=ax.transAxes, bbox = dict(props.items(),edgecolor=e[2]),zorder=11)
        ax.text(0.025,.975,'wet & cold:\n{0:2.1f}% ({1:2.1f}%)'.format(fc_probs[3],clim_probs[3]),va='top',ha='left',fontsize=15,transform=ax.transAxes, bbox = dict(props.items(),edgecolor=e[3]),zorder=11)

    # axis labels and title:
    ax.set_xlabel('{0:s} [{1:s}]'.format(x_var_name.replace('_',' '),x_units),fontsize=18)
    ax.set_ylabel('{0:s} [{1:s}]'.format(y_var_name.replace('_',' '),y_units),fontsize=18)
    ax.set_title(title,fontsize=24,y=1.1)

    if print_n:
        N = len(x_ensemble)
        ax.text(.93,1.01,'N = {N:d}'.format(N=N),va='bottom',ha='left',fontsize=13,transform=ax.transAxes)

    ax.tick_params(axis='x', labelsize=15)
    ax.tick_params(axis='y', labelsize=15)

    # save if path is specified:
    if save_path is not None:
        if fig_name is None:
            fig_name = 'unnamed'
        fig_name_full = os.path.join(save_path,fig_name)
        # save both as png and as pdf
        print('writing {0:s}.png'.format(fig_name_full))
        f.savefig(fig_name_full + '.png',dpi=300,bbox_inches='tight')
        # f.savefig(fig_name_full + '.pdf',bbox_inches='tight')
        plt.close(f)