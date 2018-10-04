#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 14:14:42 2018

@author: dmelgarm
"""

from obspy import Stream,Trace,UTCDateTime
from numpy import genfromtxt,where,array
from gnssQC import geodetics
import json

#define site list of stations to be processed and json file with days data
sitelist='/home/dmelgarm/code/PANGA/site_list/readi_sitelist.txt'
#json_file='/home/dmelgarm/PANGA_test/test_small.txt'
json_file='/home/dmelgarm/PANGA_test/test'

path_out='/home/dmelgarm/PANGA_test/'

#Whose data am I looking at
net='CW'

#start time
t0=UTCDateTime('2018-10-03T00:00:00Z')

#How many and what stations are we reading today?
stations=genfromtxt(sitelist,usecols=0,dtype='U')

#Get a priori coordinates
ref_x=genfromtxt(sitelist,usecols=1)
ref_y=genfromtxt(sitelist,usecols=2)
ref_z=genfromtxt(sitelist,usecols=3)

#Rotate a priori coordinates to lon,lat,alt
ref_lon,ref_lat,ref_alt=geodetics.ecef2lla(ref_x,ref_y,ref_z)

#Generate list of empty streams, one stream per station, this list will be ordered
#according to the same order of "stations" from the sitelist variable
east_list=[]
north_list=[]
up_list=[]
for k in range(len(stations)):
    east_list.append(Stream())
    north_list.append(Stream())
    up_list.append(Stream())
    
#now read one line at a time, make a tiny trace object, assign to correct stream
with open(json_file) as f:
    for line in f:
        data=json.loads(line)
        
        #parse data
        sta=data['site']
        x=data['x']
        y=data['y']
        z=data['z']
        t=data['t']
        
        #convert from UNIX time to UTC
        t=UTCDateTime(t)
        
        #Find reference ECEF coordinates and reference lat and lon, this index will
        #also be used to find correct stream object to append tiny trace to
        i=where(data['site'].lower()==stations)[0][0]
        sta_lon=ref_lon[i]
        sta_lat=ref_lat[i]
        sta_x=ref_x[i]
        sta_y=ref_y[i]
        sta_z=ref_z[i]
        
        #Rotate from Earth Centered Earth Fixed to local NEU
        n,e,u=geodetics.rotate2neu(x,y,z,sta_x,sta_y,sta_z,sta_lon,sta_lat)
        print('%s\t%s\t%f\t%f\t%f' % (data['site'],t,n,e,u))
        
        #create trace objects append to pertinent stream
        ntr=Trace()
        etr=Trace()
        utr=Trace()
        
        ntr.data=array([n])
        etr.data=array([e])
        utr.data=array([u])
        
        #Add some metadata, time and statoin name and lon/lat
        ntr.stats.starttime=t
        ntr.stats.station=sta.lower()
        ntr.stats.network=net
        ntr.stats.channel='LXN'
        ntr.stats.delta=1.0
        
        etr.stats.starttime=t
        etr.stats.station=sta.lower()
        etr.stats.network=net
        etr.stats.channel='LXE'
        ntr.stats.delta=1.0
        
        utr.stats.starttime=t
        utr.stats.station=sta.lower()
        utr.stats.network=net
        utr.stats.channel='LXZ'
        utr.stats.delta=1.0
        
        #use correct index to find the relevant stream object to append to
        east_list[i]+=etr
        north_list[i]+=ntr
        up_list[i]+=utr
        
#now merge all the traces into one single big trace
for k in range(len(east_list)):
    print('... merging station '+east_list[k].stats.station)
    east_list[k].merge(fill_value=9999)
    north_list[k].merge(fill_value=9999)
    up_list[k].merge(fill_value=9999)
    
    #trim only to pertinent day
    print('... trimming station '+east_list[k].stats.station)
    east_list[k].trim(starttime=t0,endtime=t0+86400)
    north_list[k].trim(starttime=t0,endtime=t0+86400)
    p_list[k].trim(starttime=t0,endtime=t0+86400)
    
    #write to file
    print('... writing station '+east_list[k].stats.station)
    file_out=path_out+east_list[k].stats.station+'.LXE.mseed'
    east_list[k].write(file_out,format='MSEED')
    file_out=path_out+north_list[k].stats.station+'.LXN.mseed'
    north_list[k].write(file_out,format='MSEED')
    file_out=path_out+up_list[k].stats.station+'.LXZ.mseed'
    up_list[k].write(file_out,format='MSEED')
    
print('Done with conversion to MSEED of all files')
    
    

