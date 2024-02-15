#!/bin/bash
# check if the script has already successfully executed this month (which is the case if the below file exists),
# only execute if the file does not exist

conda_path=/nird/home/owul/miniforge3

if [ ! -e /projects/NS9001K/owul/projects/cf_monthly_forecast/data/index/complete_biv_$(date +%Y)-$(date +%m).ix ]
then
source $conda_path/etc/profile.d/conda.sh
# activate the environment:
conda activate cf_fresh
# run plotting routine:
ipython /projects/NS9001K/owul/projects/cf_monthly_forecast/cf_monthly_forecast/bivariate_plots.py
fi

# Conduct a similar check for the probability plots.
if [ ! -e /projects/NS9001K/owul/projects/cf_monthly_forecast/data/index/complete_$(date +%Y)-$(date +%m).ix ]
then
source $conda_path/etc/profile.d/conda.sh
# activate the environment:
conda activate cf_fresh
# run plotting routine:
ipython /projects/NS9001K/owul/projects/cf_monthly_forecast/notebooks/002_forecast_plots.py
fi

# Conduct a similar check for the anomaly plots.
# This is separated from the above since anomaly plots depend on the existence of (multiple)
# different files!

if [ ! -e /projects/NS9001K/owul/projects/cf_monthly_forecast/data/index/complete_anom_$(date +%Y)-$(date +%m).ix ]
then
source $conda_path/etc/profile.d/conda.sh
# activate the environment:
conda activate cf_fresh
# run plotting routine:
ipython /projects/NS9001K/owul/projects/cf_monthly_forecast/notebooks/004_forecast_anomalies.py
fi

FC_FILENAME='forecast_'$(date +%Y)_$(date +%-m)'.nc4'
# copy the forecast summary file to the public folder if it isn't there yet:
if [ ! -e /projects/NS9873K/www/CF_seasonal_fc/$FC_FILENAME -a -e /projects/NS9873K/DATA/SFE/Forecasts/$FC_FILENAME ]
then
cp /projects/NS9873K/DATA/SFE/Forecasts/$FC_FILENAME /projects/NS9873K/www/CF_seasonal_fc/
# give reading rights to all users
chmod 664 /projects/NS9873K/www/CF_seasonal_fc/$FC_FILENAME
else
echo File already exists on web-exposed folder.
fi