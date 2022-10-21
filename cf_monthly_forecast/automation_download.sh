#!/bin/bash
# try downloading the latest seasonal forecast (& corr. hindcast data if needed) from the Climate Data Store: 

if [ ! -e /projects/NS9001K/owul/projects/cf_monthly_forecast/data/index/dl/dl_complete_$(date +%Y)-$(date +%m).ix ]
then
source /nird/home/owul/miniconda3/etc/profile.d/conda.sh # look for <base_path>/etc/profile.d/conda.sh in <base_path> given by conda info | grep -i 'base environment'
# activate the environment:
conda activate cf_monthly_forecast
# run plotting routine:
ipython /projects/NS9001K/owul/projects/cf_monthly_forecast/cf_monthly_forecast/download_monthly_operational.py
fi