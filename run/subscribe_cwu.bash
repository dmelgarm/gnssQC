#!/bin/bash

#This script gets the current day of year, creates a new daily data folder,
#and inits the rabbitMQ subscription script. This script should run at 11pm UTC
#of the day BEFORE so that you catch one hours worth of data before the start
#of the day of interest. The excess data will be cleaned up later in another
#python script that converts the json to MSEED


#where am I working?
home=/home/dmelgarm/RTGNSS/cwu/mseed/

#What day of year is it?
current_day=$(date +%j)

#Add one
current_day=`echo $current_day+1 | bc`

#create daily directory
mkdir -p home+current_day
