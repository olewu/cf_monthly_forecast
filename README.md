CF_monthly_forecast
==============================
[![Build Status](https://github.com/olewu/cf_monthly_forecast/workflows/Tests/badge.svg)](https://github.com/olewu/cf_monthly_forecast/actions)
[![codecov](https://codecov.io/gh/olewu/cf_monthly_forecast/branch/main/graph/badge.svg)](https://codecov.io/gh/olewu/cf_monthly_forecast)
[![License:MIT](https://img.shields.io/badge/License-MIT-lightgray.svg?style=flt-square)](https://opensource.org/licenses/MIT)
<!-- [![pypi](https://img.shields.io/pypi/v/cf_monthly_forecast.svg)](https://pypi.org/project/cf_monthly_forecast) -->
<!-- [![conda-forge](https://img.shields.io/conda/dn/conda-forge/cf_monthly_forecast?label=conda-forge)](https://anaconda.org/conda-forge/cf_monthly_forecast) -->
<!--[![Documentation Status](https://readthedocs.org/projects/cf_monthly_forecast/badge/?version=latest)](https://cf_monthly_forecast.readthedocs.io/en/latest/?badge=latest)-->


Production of Climate Futures monthly multi-model forecasts and visualization (can run automatically on Sigma2's NIRD server)

## Installation

First, clone the environment to a place of your choice.

Install a conda environment with the minimum requirements by running:

`conda env create -f env_mini.yml --name cf_forecast`

To install the package's functionality, run the following from the project root directory with the `cf_forecast` environment activated:

`pip install -e .`

The `-e` option installs the package in editable mode, so any change you make will be effective as soon as you re-import the package (no need to re-install).

## Configuration

To be able to download data from the CDS, you need a user account at [Copernicus](https://cds.climate.copernicus.eu/#!/home).

The data paths are currently configured to work on Sigma2's [NIRD system](https://documentation.sigma2.no/files_storage/nird.html) only. A lot of the functionality relies on the way that the forecast data are saved on NIRD. 

In `cf_monthly_forecast/config.py`, you can set the email address to your own. Some scripts send emails on the status of their execution and if this address is not set, you will not get them.

## Functionality
### Workflow for downloads:

`cf_monthly_forecast/automation_download.sh` is scheduled (crontab) to regularly run every hour at 00 minutes from the 13th to the 23rd of every month. 

`cf_monthly_forecast/automation_download.sh` executes `cf_monthly_forecast/download_monthly_operational.py` whose output is logged in `logs/download_monthly_oper_<init_year>_<init_month>.log`. The routine goes through all forecast models and tries to retrieve the latest forecast. If one model does not exist, it will try the next one. For each successful download, a file is written in `data/index/dl/dl_complete_<model>_<init_year>-<init_month>.ix`. If all models were downloaded correctly, another file `data/index/dl/dl_complete_<init_year>-<init_month>.ix` is created. Once this file exists, `cf_monthly_forecast/automation_download.sh` will not execute `cf_monthly_forecast/download_monthly_operational.py` any longer.


### Workflow for figure production:

`cf_monthly_forecast/automation.sh` is scheduled (crontab) to regularly run every hour at 50 minutes from the 13th to the 23rd of every month. 

`cf_monthly_forecast/automation.sh` executes three plotting scripts `cf_monthly_forecast/bivariate_plots.py` (local temperature vs. precipitation plots), `notebooks/002_forecast_plots.py` (forecast probabilities) and `notebooks/004_forecast_anomalies.py` (forecast anomalies) whose output is logged in `logs/fc_bivariate_plt.log`, `logs/fc_monthly_plt.log` and `logs/fc_monthly_anom_plt.log`, respectively. Each plotting routine depends on the existence of a different forecast file from the production, so it is possible that anomaly plots are prodcued but no bivariate plots[^1]. When a plotting routine has executed without error, a file `data/index/complete_biv_<init_year>-<init_month>.ix` (`data/index/complete_<init_year>-<init_month>.ix`, `data/index/complete_anom_<init_year>-<init_month>.ix` is created. Once this file exists, `cf_monthly_forecast/automation_download.sh` will not automatically execute the respective plotting scripts any longer! This means that if there is a new version of the production files or some changes in the plots are desired, the abovementioned scripts have to be manually executed again.

[^1]: Ideally, the bivariate plots are produced first as they rely on a file that currently is the only one that contains information on the systems that made it into the MME. If that file exists, the systems will be derived and saved for the respective initialization. Note that it could be that the other files are there first, in which case the anomaly and/or probability plots will be produced prior to the bivariate ones. In that case, all 6 possible systems (ECMWF, UKMO, BCCR, CMCC, DWD, MeteoFrance) will be written into the maps even though they might not all be part of the MME.

--------

<p><small>Project based on the <a target="_blank" href="https://github.com/jbusecke/cookiecutter-science-project">cookiecutter science project template</a>.</small></p>
