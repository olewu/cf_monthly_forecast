# move plotting functions from 002_forecast_plots.py and 004_forecast_anomalies.py here to make those more readable

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

from cf_monthly_forecast.config import *

def derive_abs_limits(x_da,y_da):
    """
    """
    
    x_center = x_da.climatology.values
    y_center = y_da.climatology.values

    x_pm = 3.5*x_da.sd.values
    y_pm = 3.5*y_da.sd.values

    return [x_center-x_pm,x_center+x_pm,y_center-y_pm,y_center+y_pm]

def bivariate_fc_plot(
        x_ensemble,
        y_ensemble,
        x_clim_mean,
        y_clim_mean,
        fc_probs,
        clim_probs = None,
        plt_lims = None,
        save_path = None,
        fig_name = None,
        x_var_name = 'X',
        y_var_name = 'Y',
        x_units = None, # if None, will be derived from config
        y_units = None, # if None, will be derived from config
        x_fac = None, # if None, will be derived from config, set to 1 to force no scaling
        y_fac = None, # if None, will be derived from config, set to 1 to force no scaling
        title = ''
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
    
    if 'precipitation' in x_var_name:
        plt_lims[0] = -.0001
        x_ensemble[x_ensemble < 0] = 0
    if 'precipitation' in y_var_name:
        plt_lims[2] = -.0001
        y_ensemble[y_ensemble < 0] = 0
    
    ax.scatter(x_ensemble,y_ensemble,marker='o',color='none',edgecolor='C0',clip_on=True)

    if plt_lims is None:
        xlims = ax.get_xlim(); ylims = ax.get_ylim()
    else:
        xlims = [pl*x_fac+x_offs for pl in plt_lims[:2]]
        ylims = [pl*y_fac+y_offs for pl in plt_lims[2:]]

        ax.set_xlim(xlims)
        ax.set_ylim(ylims)

    ax.vlines(x_clim_mean,ylims[0],ylims[1],color='k',ls='dashed',lw=2)
    ax.hlines(y_clim_mean,xlims[0],xlims[1],color='k',ls='dashed',lw=2)
    ax.vlines(x_em,ylims[0],ylims[1],color='C0',lw=2)
    ax.hlines(y_em,xlims[0],xlims[1],color='C0',lw=2)

    # annotate:
    props = dict(boxstyle='round', facecolor='w', alpha=0.5,lw=2)
    e = ['k','k','k','k']
    max_prob_arg = np.array(fc_probs).argmax()
    # highlight box with highest chance of occurrence:
    e[max_prob_arg] = 'r'

    if clim_probs is None:
        ax.text(.975,.975,'wet & warm:\n{0:2.1f}%'.format(fc_probs[0]),va='top',ha='right',fontsize=15,transform=ax.transAxes, bbox = dict(props.items(),edgecolor=e[0]))
        ax.text(.975,.025,'dry & warm:\n{0:2.1f}%'.format(fc_probs[1]),va='bottom',ha='right',fontsize=15,transform=ax.transAxes, bbox = dict(props.items(),edgecolor=e[1]))
        ax.text(0.025,.025,'dry & cold:\n{0:2.1f}%'.format(fc_probs[2]),va='bottom',ha='left',fontsize=15,transform=ax.transAxes, bbox = dict(props.items(),edgecolor=e[2]))
        ax.text(0.025,.975,'wet & cold:\n{0:2.1f}%'.format(fc_probs[3]),va='top',ha='left',fontsize=15,transform=ax.transAxes, bbox = dict(props.items(),edgecolor=e[3]))
    else:
        ax.text(.975,.975,'wet & warm:\n{0:2.1f}% ({1:2.1f}%)'.format(fc_probs[0],clim_probs[0]),va='top',ha='right',fontsize=15,transform=ax.transAxes, bbox = dict(props.items(),edgecolor=e[0]))
        ax.text(.975,.025,'dry & warm:\n{0:2.1f}% ({1:2.1f}%)'.format(fc_probs[1],clim_probs[1]),va='bottom',ha='right',fontsize=15,transform=ax.transAxes, bbox = dict(props.items(),edgecolor=e[1]))
        ax.text(0.025,.025,'dry & cold:\n{0:2.1f}% ({1:2.1f}%)'.format(fc_probs[2],clim_probs[2]),va='bottom',ha='left',fontsize=15,transform=ax.transAxes, bbox = dict(props.items(),edgecolor=e[2]))
        ax.text(0.025,.975,'wet & cold:\n{0:2.1f}% ({1:2.1f}%)'.format(fc_probs[3],clim_probs[3]),va='top',ha='left',fontsize=15,transform=ax.transAxes, bbox = dict(props.items(),edgecolor=e[3]))

    # axis labels and title:
    ax.set_xlabel('{0:s} [{1:s}]'.format(x_var_name.replace('_',' '),x_units),fontsize=18)
    ax.set_ylabel('{0:s} [{1:s}]'.format(y_var_name.replace('_',' '),y_units),fontsize=18)
    ax.set_title(title,fontsize=24,y=1.025)

    ax.tick_params(axis='x', labelsize=15)
    ax.tick_params(axis='y', labelsize=15)

    # save if path is specified:
    if save_path is not None:
        if fig_name is None:
            fig_name = 'unnamed'
        fig_name_full = os.path.join(save_path,fig_name)
        # save both as png and as pdf
        f.savefig(fig_name_full + '.png',dpi=300,bbox_inches='tight')
        # f.savefig(fig_name_full + '.pdf',bbox_inches='tight')
        plt.close(f)