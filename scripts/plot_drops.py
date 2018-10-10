#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 16:40:25 2018

@author: dmelgarm
"""

from glob import glob
from numpy import genfromtxt,where,zeros,arange,r_,array,expand_dims,c_,nan
from matplotlib import pyplot as plt

folders=glob('/home/dmelgarm/RTGNSS/cwu/mseed/2018/*')
site_list='/home/dmelgarm/code/PANGA/site_list/readi_sitelist.txt'
stations=genfromtxt(site_list,usecols=0,dtype='U')

vmin=50
vmax=100

#output
Nreceived=zeros(len(stations))
Ndropped=zeros(len(stations))

#loop over all stations get ercent recevied
for ksta in range(len(stations)):
    
    site=stations[ksta]
    print('Working on '+stations[ksta])
    
    for kday in range(len(folders)):
        
        #Avoid folders with no data
        if folders[kday]=='/home/dmelgarm/RTGNSS/cwu/mseed/2018/283' or folders[kday]=='/home/dmelgarm/RTGNSS/cwu/mseed/2018/283':
            pass
        
        else:

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
fig, axarr = plt.subplots(1,5)
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
    
plt.suptitle('Data arrival to UO (%)\nExchange: CWU\nday 277 - day 282')    

