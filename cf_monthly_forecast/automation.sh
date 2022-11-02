#!/bin/bash
# check if the script has already successfully executed this month (which is the case if the below file exists),
# only execute if the file does not exist

if [ ! -e /projects/NS9001K/owul/projects/cf_monthly_forecast/data/index/complete_$(date +%Y)-$(date +%m).ix ]
then
source /nird/home/owul/miniconda3/etc/profile.d/conda.sh # look for <base_path>/etc/profile.d/conda.sh in <base_path> given by conda info | grep -i 'base environment'
# activate the environment:
conda activate cf_monthly_forecast
# run plotting routine:
ipython /projects/NS9001K/owul/projects/cf_monthly_forecast/notebooks/002_forecast_plots.py
fi

# Conduct a similar check for the anomaly plots.
# This is separated from the above since anomaly plots depend on the existence of (multiple)
# different files!

if [ ! -e /projects/NS9001K/owul/projects/cf_monthly_forecast/data/index/complete_anom_$(date +%Y)-$(date +%m).ix ]
then
source /nird/home/owul/miniconda3/etc/profile.d/conda.sh # look for <base_path>/etc/profile.d/conda.sh in <base_path> given by conda info | grep -i 'base environment'
# activate the environment:
conda activate cf_monthly_forecast
# run plotting routine:
ipython /projects/NS9001K/owul/projects/cf_monthly_forecast/notebooks/004_forecast_anomalies.py
fi

# Conduct a similar check for the bivariate plots.
if [ ! -e /projects/NS9001K/owul/projects/cf_monthly_forecast/data/index/complete_biv_$(date +%Y)-$(date +%m).ix ]
then
source /nird/home/owul/miniconda3/etc/profile.d/conda.sh # look for <base_path>/etc/profile.d/conda.sh in <base_path> given by conda info | grep -i 'base environment'
# activate the environment:
conda activate cf_monthly_forecast
# run plotting routine:
ipython /projects/NS9001K/owul/projects/cf_monthly_forecast/cf_monthly_forecast/bivariate_plots.py
fi

FC_FILENAME='forecast_'$(date +%Y)_$(date +%m)'.nc4'
# copy the forecast summary file to the public folder if it isn't there yet:
if [ ! -e /projects/NS9853K/www/CF_seasonal_fc/$FC_FILENAME -a -e /projects/NS9853K/DATA/SFE/Forecasts/$FC_FILENAME ]
then
cp /projects/NS9853K/DATA/SFE/Forecasts/$FC_FILENAME /projects/NS9853K/www/CF_seasonal_fc/
# give reading rights to all users
chmod 664 /projects/NS9853K/www/CF_seasonal_fc/$FC_FILENAME
fi