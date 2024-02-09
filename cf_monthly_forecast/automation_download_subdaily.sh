#!/bin/bash
# try downloading the latest seasonal forecast (& corr. hindcast data if needed) from the Climate Data Store: 

if [ ! -e /projects/NS9001K/owul/projects/cf_monthly_forecast/data/index/dl/dl_subdaily_complete_$(date +%Y)-$(date +%m).ix ]
then
source $(conda info | grep -i 'base environment' | awk '{print $4}')/etc/profile.d/conda.sh
# activate the environment:
conda activate cf_fresh
# run plotting routine:
ipython /projects/NS9001K/owul/projects/cf_monthly_forecast/cf_monthly_forecast/download_daily_operational.py
fi