#!/bin/bash
# try downloading the latest seasonal forecast (& corr. hindcast data if needed) from the Climate Data Store: 

date

conda_path=/nird/home/owul/miniforge3

if [ ! -e /projects/NS9001K/owul/projects/cf_monthly_forecast/data/index/dl/dl_complete_$(date +%Y)-$(date +%m).ix ]
then
source $conda_path/etc/profile.d/conda.sh
# activate the environment:
conda activate cf_fresh
# run plotting routine:
ipython /projects/NS9001K/owul/projects/cf_monthly_forecast/cf_monthly_forecast/download_monthly_operational.py
fi