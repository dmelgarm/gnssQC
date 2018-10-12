#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 14:34:16 2018

@author: dmelgarm
"""

#Because we're running from a cron with limited path access, need to manually add
#relevant directories
import sys
sys.path.append('/home/dmelgarm/code/anaconda3/lib/python3.6/site-packages/')
sys.path.append('/home/dmelgarm/code/')

#Set up a backend that does not show plot to user
import matplotlib
matplotlib.use('Agg')

#Now the other modules
from gnssQC import analysis
from numpy import genfromtxt,where,zeros,arange,r_,array,expand_dims,c_,nan
from matplotlib import pyplot as plt
from obspy import read
import argparse
from os.path import exists




##############     parse the command line       ###############################

parser = argparse.ArgumentParser()
parser.add_argument("--net", help="CW, SI, JP, or RK")
parser.add_argument("--exchange", help="CWU, SIO, JPL or READI")
parser.add_argument("--doy_start", help="First day of year")
parser.add_argument("--working_dir", help="Path to mseed folders")
parser.add_argument("--sitelist", help="Path to station sitelist")
args = parser.parse_args()

#assign argumens to variables
delta_day=5
net=args.net
exchange=args.exchange
site_list=args.sitelist
working_dir=args.working_dir
days=arange(int(args.doy_start),int(args.doy_start)+5)-delta_day+1

print(net)
print(exchange)
print(site_list)
print(working_dir)
print(days)

##############       done parsing       #######################################



################        What do you want to do?    ############################

find_dropouts=True
plot_dropouts_table=True
plot_histogram_time_of_day=True

#################     done with pre-amble stuff    ############################




#folders with data
folders=[]
for k in range(delta_day):
    day_folder=working_dir+str(days[k])
    if exists(day_folder)==True:
        folders.append(day_folder)
    else:
        print('... folder %s has no data' % (day_folder))
print(folders)

#read stations
stations=genfromtxt(site_list,usecols=0,dtype='U')



# Generate dropouts ZXD mseed files and _drops.summary table
if find_dropouts:
    for kday in range(len(folders)):
        
        print('Finding dropouts for data in '+folders[kday])
        analysis.get_dropouts(stations,folders[kday]+'/',net)
      
        
        
        
# from _drops.summary for all days plot a table
if plot_dropouts_table:
    vmin=70
    vmax=150
    
    #output
    Nreceived=zeros(len(stations))
    Ndropped=zeros(len(stations))
    
    #loop over all stations get ercent recevied
    for ksta in range(len(stations)):
        
        site=stations[ksta]
        print('Working on '+stations[ksta])
        
        for kday in range(len(folders)):
            
            station_drops=genfromtxt(folders[kday]+'/_drops.summary',usecols=0,dtype='U')
            
            try:
                i=where(station_drops==site)[0]
                data=genfromtxt(folders[kday]+'/_drops.summary',usecols=[1,2])
                Nreceived[ksta]+=data[i,0]
                Ndropped[ksta]+=data[i,1]
            except:

                Nreceived[ksta]+=0
                Ndropped[ksta]+=0
                
    uptime=100-Ndropped/Nreceived*100
    uptime=expand_dims(uptime,1)
    
    #draw a tbale
    fig, axarr = plt.subplots(1,5,figsize=(7,8.5))
    for kax in arange(len(axarr)):
        
        ax=axarr[kax]
        
        #which ones am I plotting
        i=arange(40*kax,40*(kax+1)-1)
        Nslice=len(i)
        
        if kax<4:
            U=c_[uptime[i],uptime[i],uptime[i]]
            S=stations[i]
            im = ax.imshow(U,cmap='gist_rainbow',vmin=vmin,vmax=vmax)
        else:
            i=arange(40*kax,len(stations))
            U=zeros(Nslice)*nan
            U[0:len(i)]=uptime[i,0]
            U=c_[expand_dims(U,1),expand_dims(U,1),expand_dims(U,1)]
            S=stations[i]
            for kfix in arange(Nslice-len(i)):
                S=r_[S,array([''])]
            im = ax.imshow(U,cmap='gist_rainbow',vmin=vmin,vmax=vmax)
            
            
        
        
        ax.set_yticks(arange(len(U)))
        ax.set_yticklabels(S)
        
        # make text
        cell_text=[]
        for k in range(len(S)):
            cell_text.append('%.2f' % (U[k,0]))
        
        for k in range(len(S)):
            text = ax.text(1.0, k, cell_text[k],ha="center", va="center", color="k")
            
        ax.set_xticks([])
        
    plt.suptitle('Data arrival to UO (%%)\nExchange: %s\nday %d - day %d' % (exchange,days[0],days[-1]))   
    plt.savefig('/home/dmelgarm/RTGNSS/plots/dropouts.'+exchange+'.png')
    plt.close()





# WHat time of day do the dropouts happen at?
if plot_histogram_time_of_day:
    
    #loop over all stations get ercent recevied
    for ksta in range(len(stations)):
        
        site=stations[ksta]
        print('Working on '+stations[ksta])
        
        #output
        time_of_day=array([])
        
        data_exists=False
        
        for kday in range(len(days)):            
            
            try:
                drops=read(folders[kday]+'/'+site+'.ZXD.mseed')
                time_of_day=r_[time_of_day,drops[0].data]
                
                
                #Some data was found
                data_exists=True

            except:

                pass
        
        #Something was found so make the plot
        if data_exists:
            #make the plot
            plt.figure(figsize=(7,2))
            plt.hist(time_of_day/3600,24*60,label=drops[0].stats.network+'.'+drops[0].stats.station)
            plt.ylabel('Count')
            plt.xlabel('UTC time of day (hours)')
            plt.xlim([0,24])
            plt.xticks(arange(0,24))
            plt.legend()
            plt.subplots_adjust(bottom=0.25)
            plt.savefig('/home/dmelgarm/RTGNSS/plots/station_drops/'+drops[0].stats.network+'.'+drops[0].stats.station+'.png')
            plt.close()
            