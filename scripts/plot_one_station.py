#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 09:00:11 2018

@author: dmelgarm
"""

from matplotlib import pyplot as plt
from obspy import read
from numpy import arange,where,mean

station='mhcb'
channel='LXE'
days=arange(286,289)


#read CWU
for kday in range(len(days)):
    if kday==0:
        cwu=read('/home/dmelgarm/RTGNSS/cwu/mseed/2018/'+str(days[kday])+'/'+station+'.'+channel+'.mseed')
    else:
        cwu+=read('/home/dmelgarm/RTGNSS/cwu/mseed/2018/'+str(days[kday])+'/'+station+'.'+channel+'.mseed')
cwu.merge(fill_value=9999)

#read SIO
for kday in range(len(days)):
    if kday==0:
        sio=read('/home/dmelgarm/RTGNSS/sio/mseed/2018/'+str(days[kday])+'/'+station+'.'+channel+'.mseed')
    else:
        sio+=read('/home/dmelgarm/RTGNSS/sio/mseed/2018/'+str(days[kday])+'/'+station+'.'+channel+'.mseed')
sio.merge(fill_value=9999)
        
#read READI
for kday in range(len(days)):
    if kday==0:
        readi=read('/home/dmelgarm/RTGNSS/readi/mseed/2018/'+str(days[kday])+'/'+station+'.'+channel+'.mseed')
    else:
        readi+=read('/home/dmelgarm/RTGNSS/readi/mseed/2018/'+str(days[kday])+'/'+station+'.'+channel+'.mseed')
readi.merge(fill_value=9999)        
        
        
#plot
plt.close('all')
fig,axarr=plt.subplots(3,1,sharex=True,sharey=True,figsize=(16,4))

stream=readi
ax=axarr[0]
idrops=where(stream[0].data==9999)[0]
inodrops=where(stream[0].data!=9999)[0]
t=stream[0].times()/3600
d=stream[0].data
d=d-mean(d[inodrops])
d[idrops]=0
ax.plot(t,d,label='READI')
ax.scatter(t[idrops],d[idrops],c='r',s=2,label='%d drops' % (len(idrops)),zorder=9999)
ax.legend(loc=0)
ax.set_title('Station '+station+', east component')
ax.set_xlim([0,24*3])
ax.set_ylabel('m')
ax.grid()


stream=cwu
ax=axarr[1]
idrops=where(stream[0].data==9999)[0]
inodrops=where(stream[0].data!=9999)[0]
t=stream[0].times()/3600
d=stream[0].data
d=d-mean(d[inodrops])
d[idrops]=0
ax.plot(t,d,label='CWU')
ax.scatter(t[idrops],d[idrops],c='r',s=2,label='%d drops' % (len(idrops)),zorder=9999)
ax.legend(loc=0)
ax.set_xlim([0,24*3])
ax.set_ylabel('m')
ax.grid()

stream=sio
ax=axarr[2]
idrops=where(stream[0].data==9999)[0]
inodrops=where(stream[0].data!=9999)[0]
t=stream[0].times()/3600
d=stream[0].data
d=d-mean(d[inodrops])
d[idrops]=0
ax.plot(t,d,label='SIO')
ax.scatter(t[idrops],d[idrops],c='r',s=2,label='%d drops' % (len(idrops)),zorder=9999)
ax.legend(loc=0)
ax.set_xlim([0,24*3])
ax.set_xlabel('Hours')
ax.set_ylabel('m')
plt.grid()