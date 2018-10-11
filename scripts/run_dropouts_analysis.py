#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 14:34:16 2018

@author: dmelgarm
"""

from gnssQC import analysis
from glob import glob
from numpy import genfromtxt,where,zeros,arange,r_,array,expand_dims,c_,nan
from matplotlib import pyplot as plt
from obspy import read



net='CW'
exchange='CWU'
site_list='/home/dmelgarm/code/PANGA/site_list/readi_sitelist.txt'
days=arange(277,283)
working_dir='/home/dmelgarm/RTGNSS/cwu/mseed/'

################        What do you want to do?    ############################
find_dropouts=False
plot_dropouts_table=False
plot_histogram_time_of_day=True



#################     done with pre-amble stuff    ############################




#folders with data
folders=glob(working_dir+'2018/*')

#read stations
stations=genfromtxt(site_list,usecols=0,dtype='U')



# Generate dropouts ZXD mseed files and _drops.summary table
if find_dropouts:
    for kday in range(len(folders)):
        
        print('Finding dropouts for data in '+folders[kday])
        analysis.get_dropouts(stations,folders[kday]+'/',net)
      
        
        
        
# from _drops.summary for all days plot a table
if plot_dropouts_table:
    vmin=50
    vmax=100
    
    #output
    Nreceived=zeros(len(stations))
    Ndropped=zeros(len(stations))
    
    #loop over all stations get ercent recevied
    for ksta in range(len(stations)):
        
        site=stations[ksta]
        print('Working on '+stations[ksta])
        
        for kday in range(len(days)):
            
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
            im = ax.imshow(U,cmap='brg',vmin=vmin,vmax=vmax)
        else:
            i=arange(40*kax,len(stations))
            U=zeros(Nslice)*nan
            U[0:len(i)]=uptime[i,0]
            U=c_[expand_dims(U,1),expand_dims(U,1),expand_dims(U,1)]
            S=stations[i]
            for kfix in arange(Nslice-len(i)):
                S=r_[S,array([''])]
            im = ax.imshow(U,cmap='brg',vmin=vmin,vmax=vmax)
            
            
        
        
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
            