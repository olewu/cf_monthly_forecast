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


Workflow:

`automation_download.sh` and `automation.sh` are regularly run (crontab) between the 13th and 23rd of every month. 

`automation_download.sh` executes `cf_monthly_forecast/download_monthly_operational.py`.


--------

<p><small>Project based on the <a target="_blank" href="https://github.com/jbusecke/cookiecutter-science-project">cookiecutter science project template</a>.</small></p>
