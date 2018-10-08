#!/bin/bash

# Diego Melgar
# University of Oregon
# October, 2018

#This script gets the current day of year, creates a new daily data folder,
#and inits the rabbitMQ subscription script. This script should run at 11pm UTC
#of the day BEFORE so that you catch one hours worth of data before the start
#of the day of interest. The excess data will be cleaned up later in another
#python script that converts the json to MSEED. Run this script using a cron.

#where is the subscription script
path_to_code=/home/dmelgarm/code/PANGA/script/

#config file and sitelist
config_file=/home/dmelgarm/code/PANGA/conf/rmq-x-cwu-xyzcov.cfg
sitelist=/home/dmelgarm/code/PANGA/site_list/readi_sitelist.txt

#where am I working?
home=/home/dmelgarm/RTGNSS/cwu/mseed/

#What year is it
year=`date +"%Y"`

#What day of year is it?
current_day=$(date +%j)

#Add one because this wil be "tomorrow's" data
current_day=`echo $current_day+1 | bc`

#create daily directory (if it doesn't exis)
working_dir=$home$year/$current_day/
mkdir -p $working_dir

#define output files
json_file=${working_dir}_json
error_file=${working_dir}_err.log
status_file=${working_dir}_status.log

#make a note that you are starting
utc_date=`date -u`
echo Started RabbitMQ subscription on $utc_date > $status_file

#run subscription command, use timeout to kill the subscription after 24 and 20 minutes
# this gives you 1hr before start of day and one hour after
timeout 1460m ${path_to_code}subscribe.py --rabbitmq-configuration $config_file --sitelist $sitelist > $json_file 2> $error_file &

