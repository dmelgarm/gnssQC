#!/bin/bash

# Run one day's worth of data through json2MSEED
sitelist=/home/dmelgarm/code/PANGA/site_list/readi_sitelist.txt
working_dir=/home/dmelgarm/RTGNSS/cwu/mseed/2018/286/
net=CW
#Day needs to be one moreo if you want to run 10/12 it should be 10/13
start_time=2018-10-14T00:00:00Z
# Run it
/home/dmelgarm/code/anaconda3/bin/python /home/dmelgarm/code/gnssQC/json2seed.py --sitelist $sitelist --datapath $working_dir --net $net --starttime $start_time


# Run one day's worth of data through json2MSEED
sitelist=/home/dmelgarm/code/PANGA/site_list/readi_sitelist.txt
working_dir=/home/dmelgarm/RTGNSS/cwu/mseed/2018/287/
net=CW
#Day needs to be one moreo if you want to run 10/12 it should be 10/13
start_time=2018-10-15T00:00:00Z
# Run it
/home/dmelgarm/code/anaconda3/bin/python /home/dmelgarm/code/gnssQC/json2seed.py --sitelist $sitelist --datapath $working_dir --net $net --starttime $start_time
