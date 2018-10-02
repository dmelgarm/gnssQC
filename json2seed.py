#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 14:14:42 2018

@author: dmelgarm
"""

from obspy import Stream,Trace,UTCDateTime
from numpy import genfromtxt,where
from gnssQC import geodetics
import json

#define site list of stations to be processed and json file with days data
sitelist='/home/dmelgarm/code/PANGA/site_list/readi_sitelist.txt'
#json_file='/home/dmelgarm/PANGA_test/test_small.txt'
json_file='/home/dmelgarm/PANGA_test/test'

#How many and what stations are we reading today?
stations=genfromtxt(sitelist,usecols=0,dtype='U')

#Get a priori coordinates
ref_x=genfromtxt(sitelist,usecols=1)
ref_y=genfromtxt(sitelist,usecols=2)
ref_z=genfromtxt(sitelist,usecols=3)

#Rotate a priori coordinates to lon,lat,alt
ref_lon,ref_lat,ref_alt=geodetics.ecef2lla(ref_x,ref_y,ref_z)

#Generate list of empty streams, one stream per station
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
        
        #convert from UNIX time top UTC
        t=UTCDateTime(t)
        
        #Find refernce ECEF coordinates and reference lat and lon
        i=where(data['site'].lower()==stations)[0][0]
        sta_lon=ref_lon[i]
        sta_lat=ref_lat[i]
        sta_x=ref_x[i]
        sta_y=ref_y[i]
        sta_z=ref_z[i]
        
        #Rotate from Earteh Centered Earth Fixed to local NEU
        n,e,u=geodetics.rotate2neu(x,y,z,sta_x,sta_y,sta_z,sta_lon,sta_lat)
        print('%s\t%f\t%f\t%f' % (data['site'],n,e,u))