#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  8 14:23:07 2018

@author: dmelgarm
"""






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
    
    #How many samples?
    Nsamples=st[0].stats.npts
    
    return(t0,seconds,Nsamples)



def ppsd(mseed_file,drop_value=9999):
    '''
    Get ppsd for one day file
    '''
    
    from obspy.signal import PPSD
    from obspy import read
    from numpy import where,mean,random
    
    #get data
    st=read(mseed_file)
#    st[0].data=random.normal(0, 0.1, size=st[0].stats.npts)
    
    #find gaps and not gaps
    gaps=where(st[0].data==drop_value)[0]
    not_gaps=where(st[0].data!=drop_value)[0]
    
    #Find mean wthout taking gaps into account and remove it
    bias=mean(st[0].data[not_gaps])
    st[0].data=st[0].data-bias
    
    #zero out gaps
    st[0].data[gaps]=0
    
    #define frequency response
    paz = {'gain': 1.0,'sensitivity': 1.0,'poles': [1,],'zeros': [0j, 0j]}
    
    #initalize ppsd object
    ppsd = PPSD(st[0].stats, paz,db_bins=(-60, 10, 0.5),period_limits=[2,600],special_handling='ringlaser')
    
    #add to ppsd
    ppsd.add(st)



def get_dropouts(stations,working_dir,net):
    '''
    loop over all sites get drops, put in an mseed file
    
    '''

    from obspy import Stream,Trace
    
    #Summary file
    f=open(working_dir+'_drops.summary','w')
    f.write('# Station, samples streamed, samples dropped, % received\n')
    
    for k in range(len(stations)):
        
        station_file=working_dir+stations[k]+'.LXE.mseed'
        
        try:
            print('... getting dropputs for'+station_file)
            t0,drops,Nsamples=dropouts(station_file)
            st=Stream(Trace())
            st[0].data=drops
            st[0].stats.starttime=t0
            st[0].stats.delta=1.0
            st[0].stats.station=stations[k]
            st[0].stats.network=net
            st[0].stats.channel='ZXD'
            out_file=working_dir+stations[k]+'.'+st[0].stats.channel+'.mseed'
            st[0].write(out_file,format='MSEED')
            
            #add to summary file
            line='%s\t%d\t%d\t%.1f\n' % (stations[k],Nsamples,len(drops),100-100*len(drops)/Nsamples)
            f.write(line)
        except:
            print('... no data for'+station_file)
            
    f.close()
    
    


    
    
    