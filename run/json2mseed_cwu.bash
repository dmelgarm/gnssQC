#!/bin/bash

#This script should run at 1:30am of the day AFTER the day of interest whose data 
#was collected from the RabbitMQ exchange by the subscription script. It will obtain
#the necessary arguemnts and pass them into json2mseed.py, this python script will in
#turn use obspy commands to conver the json for every station and every channel to 
#one big daily MSEED file

#Add to PYTHONPATH
export PYTHONPATH=/home/dmelgarm/code/anaconda3/bin
export PYTHONPATH=/home/dmelgarm/code/anaconda3/lib/python3.6/site-packages/
export PYTHONPATH=/home/dmelgarm/code
export PYTHONPATH=/home/dmelgarm/code/PANGA/lib
export PYTHONPATH=/home/dmelgarm/code/MudPy/src/python
export PYTHONPATH=/home/dmelgarm/code/clawpack-5.4.1
export PYTHONPATH=/home/dmelgarm/RTGNSS/cwu/mseed/2018/278
export PYTHONPATH=/home/dmelgarm/code/anaconda3/lib/python36.zip
export PYTHONPATH=/home/dmelgarm/code/anaconda3/lib/python3.6
export PYTHONPATH=/home/dmelgarm/code/anaconda3/lib/python3.6/lib-dynload
export PYTHONPATH=/home/dmelgarm/code/anaconda3/lib/python3.6/site-packages
export PYTHONPATH=/home/dmelgarm/code/anaconda3/lib/python3.6/site-packages/IPython/extensions

#Define site list of stations to be processed
sitelist=/home/dmelgarm/code/PANGA/site_list/readi_sitelist.txt

#Whose data am I looking at
net='CW'

#where am I working?
home=/home/dmelgarm/RTGNSS/cwu/mseed/

#What year/month/day is it
year=`date +"%Y"`

#What day of year is it?
current_day=$(date -u +%j)

# get day and month
calendar_day=$(date -u +%d)
month=$(date -u +%m)

#Subtract one because this wil be "yesterday's" data
#Only possibility of error is if it's Jan 1st in which case we
#need to make doy be 365 and year be year-1
if [ "$current_day" -eq "1" ]
then
	current_day=365
	year=`echo $year-1 | bc`
	calendar_day=31
	month=12
	start_time=$year-$month-${calendar_day}T00:00:00Z
else
	current_day=`echo $current_day-1 | bc`
	start_time=$year-$month-${calendar_day}T00:00:00Z
fi




#define daily directory where json data should be found
working_dir=$home$year/$current_day/

#log files
error_file=${working_dir}_err_json2mseed.log
status_file=${working_dir}_status_json2mseed.log

#Run the conversion script redirect output to a log file
/home/dmelgarm/code/anaconda3/bin/python /home/dmelgarm/code/gnssQC/json2seed.py --sitelist $sitelist --datapath $working_dir --net $net --starttime $start_time > $status_file 2> $error_file &

