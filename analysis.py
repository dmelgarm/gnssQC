#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  8 14:23:07 2018

@author: dmelgarm
"""

#Because we're running from a cron with limited path access, need to manually add
#relevant directories
import sys
sys.path.append('/home/dmelgarm/code/anaconda3/lib/python3.6/site-packages/')
sys.path.append('/home/dmelgarm/code/')

#other functions
from numpy import genfromtxt





net='CW'
site_list='/home/dmelgarm/code/PANGA/site_list/readi_sitelist.txt'
working_dir='/home/dmelgarm/RTGNSS/cwu/mseed/2018/280/'

#read stations
stations=genfromtxt(site_list,usecols=0,dtype='U')




def dropouts(mseed_file,drop_value=9999):
    '''
    Return array of seconds since start of day when dropouts are found
    '''
    
    from obspy import UTCDateTime,read
    from numpy import where
    
    
    st=read(mseed_file)
    
    #find start time of that day
    t0=UTCDateTime(str(st[0].stats.starttime.year)+'-'+str(st[0].stats.starttime.month)+
                   '-'+str(st[0].stats.starttime.day)+'T00:00:00Z')
    
    #Seconds between start of record and first second of day
    delta=st[0].stats.starttime-t0
    
    #find seconds sicne the start of the RECORD not of the day necesarily
    i=where(st[0].data==drop_value)[0]
    
    #add delta to obtain secnds since start of day
    seconds=st[0].times()[i]+delta
    
    return(t0,seconds)


def get_dropouts(site_list,working_dir,net):
    '''
    loop over all sites get drops, put in an mseed file
    
    '''

    from obspy import Stream,Trace,read
    
    for k in range(len(stations)):
        
        station_file=working_dir+stations[k]+'.LXE.mseed'
        
        try:
            print('... getting dropputs for'+station_file)
            t0,drops=dropouts(station_file)
            st=Stream(Trace())
            st[0].data=drops
            st[0].stats.starttime=t0
            st[0].stats.delta=1.0
            st[0].stats.station=stations[k]
            st[0].stats.network=net
            st[0].stats.channel='ZXD'
            out_file=working_dir+stations[k]+'.'+st[0].stats.channel+'.mseed'
            st[0].write(out_file,format='MSEED')
        except:
            print('... no data for'+station_file)
    
    


    
    
    