#!/bin/bash
# check if the script has already successfully executed this month (which is the case if the below file exists),
# only execute if the file does not exist
if [ ! -e /projects/NS9001K/owul/projects/cf_monthly_forecast/data/index/complete_$(date +%Y)-$(date +%-m).ix ]
then
source /nird/home/owul/miniconda3/etc/profile.d/conda.sh # look for <base_path>/etc/profile.d/conda.sh in <base_path> given by conda info | grep -i 'base environment'
# activate the environment:
conda activate cf_monthly_forecast
# run plotting routine:
ipython /projects/NS9001K/owul/projects/cf_monthly_forecast/notebooks/002_forecast_plots.py
fi