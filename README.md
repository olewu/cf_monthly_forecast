CF_monthly_forecast
==============================
[![Build Status](https://github.com/olewu/cf_monthly_forecast/workflows/Tests/badge.svg)](https://github.com/olewu/cf_monthly_forecast/actions)
[![codecov](https://codecov.io/gh/olewu/cf_monthly_forecast/branch/main/graph/badge.svg)](https://codecov.io/gh/olewu/cf_monthly_forecast)
[![License:MIT](https://img.shields.io/badge/License-MIT-lightgray.svg?style=flt-square)](https://opensource.org/licenses/MIT)[![pypi](https://img.shields.io/pypi/v/cf_monthly_forecast.svg)](https://pypi.org/project/cf_monthly_forecast)
<!-- [![conda-forge](https://img.shields.io/conda/dn/conda-forge/cf_monthly_forecast?label=conda-forge)](https://anaconda.org/conda-forge/cf_monthly_forecast) -->
<!--[![Documentation Status](https://readthedocs.org/projects/cf_monthly_forecast/badge/?version=latest)](https://cf_monthly_forecast.readthedocs.io/en/latest/?badge=latest)-->


Production of Climate Futures monthly multi-model forecasts and visualization (runs automatically on Sigma2's NIRD server)

To run the downloading, you need a user account at the CDS.

The paths are currently configured to work on Sigma2's NIRD system only.

To make this work, first clone the environment to a place of yout choice.

Install a conda environment with the minimum requirements by running:

`conda env create -f env_mini.yml --name cf_forecast`

To install the package's functionality run the following from the project root directory:

`pip install -e .`


Workflow for downloads:

`cf_monthly_forecast/automation_download.sh` and `cf_monthly_forecast/automation.sh` are scheduled (crontab) to regularly run between every 30 mins from the 13th and 23rd of every month. 

`cf_monthly_forecast/automation_download.sh` executes `cf_monthly_forecast/download_monthly_operational.py` whose output is logged in `logs/download_monthly_oper_<init_year>_<init_month>.log`. The routine goes through all forecast models and tries to retrieve the latest forecast. If one model does not exist, it will try the next one. For each successful download, a file is written in `data/index/dl/dl_complete_<model>_<init_year>-<init_month>.ix`. If all models were downloaded correctly, another file `data/index/dl/dl_complete_<init_year>-<init_month>.ix` is created. Once this file exists, `cf_monthly_forecast/automation_download.sh` will not execute `cf_monthly_forecast/download_monthly_operational.py` any longer.


Workflow for figure production:

...

--------

<p><small>Project based on the <a target="_blank" href="https://github.com/jbusecke/cookiecutter-science-project">cookiecutter science project template</a>.</small></p>
