#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 14:14:42 2018

@author: dmelgarm
"""

#Because we're running from a cron with limited path access, need to manually add
#relevant directories
import sys
sys.path.append('/home/dmelgarm/code/anaconda3/lib/python3.6/site-packages/')
sys.path.append('/home/dmelgarm/code/')

from obspy import Stream,Trace,UTCDateTime
from numpy import genfromtxt,where,array
from gnssQC import geodetics
import json
import argparse
from os import remove
from datetime import timedelta

##############     parse the command line       ###############################

parser = argparse.ArgumentParser()
parser.add_argument("--sitelist", help="Absolute path to the sitelist file")
parser.add_argument("--datapath", help="Absolute path to the DIRECTORY where the json file is held and where the converted MSEED will be saved")
parser.add_argument("--net", help="Network code of the data being processed, should be one of 'CW', 'SI', 'JP', or 'RK'")
parser.add_argument("--starttime", help="UTCDateTime fomratted string with the desired starttime of the MSEED files")
args = parser.parse_args()

#assign argumens to variables
sitelist=args.sitelist
datapath=args.datapath
net=args.net
#Make sure it's upper case
net=net.upper()

if args.starttime == None:
    t0=None
else:
    t0=UTCDateTime(args.starttime)-timedelta(days=1)
print(sitelist)
print(datapath)
print(net)
print(t0)
##############       done parsing       #######################################



###########     manual argument inputs for debugging     #######################
#sitelist='/home/dmelgarm/code/PANGA/site_list/readi_sitelist.txt'
#datapath='/home/dmelgarm/RTGNSS/cwu/mseed/2018/288/'
#net='CW'
#t0=UTCDateTime('2018-10-12T00:00:00.000000Z')
###############################################################################



#define json file to be read
json_file=datapath+'_json'

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
print('... starting JSON read')
count=0
with open(json_file) as f:
    for line in f:
        
        #print a status message
        if count % 80000 == 0:
            print('... ... working on line '+str(count))
        count+=1


        #Different rules for parsing READI vs CWU/JPL/SIO
        if net=='RK':
            #Readi records come with some weird white space, get rid of it
            data=json.loads(line.rstrip('\n').rstrip('\x00'))
            
            #Get SNCL and from that get the station code, make it lower case
            sta=data['properties']['SNCL'].split('.')[0].lower()
            
            #get coordinates, these are already N,E,U
            n,e,u=data['features'][0]['geometry']['coordinates']
            
            #Get UNIX time, it comes in milliseconds, convert to seconds
            t=data['properties']['time']/1000
    
        #Now for CWU, JPL, SIO    
        else:
            try:
                data=json.loads(line)
                
                #parse data
                sta=data['site']
                x=data['x']
                y=data['y']
                z=data['z']
                t=data['t']
            
            #If there's a json read error make time be outrageously early so the
            #rest of the calculation is skipped, it will simply later appear as a gap
            # Note, i've only seen this one or two epochs over several days
            except:
                print('*** JSON read error, skipping line')
                t='1900-01-01T00:00:00'
                sta='xxxx'
            
        #Make sure everything is the correct case
        sta=sta.lower()
            
        #convert from UNIX time to UTC
        t=UTCDateTime(t)
        
        #if present sample is past the starttime
        if t>=t0:

            #get station lon/lat from apriori list
            i=where(stations==sta)[0][0]
            sta_lon=ref_lon[i]
            sta_lat=ref_lat[i]
            
            #Now rotate coordinates
            if net=='RK':
                #Do nothing data is good to go
                pass
            
            else:
                #Find reference ECEF coordinates and reference lat and lon, this index will
                #also be used to find correct stream object to append tiny trace to
                sta_x=ref_x[i]
                sta_y=ref_y[i]
                sta_z=ref_z[i]
                
                #Rotate from Earth Centered Earth Fixed to local NEU
                n,e,u=geodetics.rotate2neu(x,y,z,sta_x,sta_y,sta_z,sta_lon,sta_lat)
            
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
            etr.stats.delta=1.0
            
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
print('... starting conversion to MSEED')
for k in range(len(east_list)):
    
    # was there any data available?
    if len(east_list[k])>0:
    
        print('... ... working on stream '+east_list[k][0].stats.station)
        east_list[k].merge(fill_value=9999)
        north_list[k].merge(fill_value=9999)
        up_list[k].merge(fill_value=9999)
        
        #trim only to pertinent day
        east_list[k].trim(starttime=t0,endtime=t0+86400)
        north_list[k].trim(starttime=t0,endtime=t0+86400)
        up_list[k].trim(starttime=t0,endtime=t0+86400)
        
        #write to file, oly if there was data left
        if len(east_list[k])>0 and len(up_list[k])>0 and len(north_list[k])>0:
            file_out=datapath+east_list[k][0].stats.station+'.LXE.mseed'
            east_list[k].write(file_out,format='MSEED')
            file_out=datapath+north_list[k][0].stats.station+'.LXN.mseed'
            north_list[k].write(file_out,format='MSEED')
            file_out=datapath+up_list[k][0].stats.station+'.LXZ.mseed'
            up_list[k].write(file_out,format='MSEED')
    
#delete big huge json file when you are done
#remove(json_file)

print('... done with conversion to MSEED of all files')
    
    

