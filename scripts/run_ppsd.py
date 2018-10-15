#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 15:54:01 2018

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
from obspy.signal import PPSD
from obspy.imaging.cm import pqlx
import argparse
from os.path import exists
from glob import glob




##############     parse the command line       ###############################

#parser = argparse.ArgumentParser()
#parser.add_argument("--net", help="CW, SI, JP, or RK")
#parser.add_argument("--exchange", help="CWU, SIO, JPL or READI")
#parser.add_argument("--day_of_year", help="First day of year")
#parser.add_argument("--working_dir", help="Path to mseed folders")
#parser.add_argument("--ppsd_dir", help="Path to PPSD objects")
#parser.add_argument("--sitelist", help="Path to station sitelist")
#args = parser.parse_args()
#
##assign argumens to variables
#net=args.net
#exchange=args.exchange
#site_list=args.sitelist
#working_dir=args.working_dir
#day_of_year=args.day_of_year
#
#print(net)
#print(exchange)
#print(site_list)
#print(mseed_dir)
#print(ppsd_dir)
#print(day_of_year)

##############       done parsing       #######################################


###########     manual argument inputs for debugging     #######################
site_list='/home/dmelgarm/code/PANGA/site_list/readi_sitelist.txt'
mseed_dir='/home/dmelgarm/RTGNSS/readi/mseed/2018'
ppsd_dir='/home/dmelgarm/RTGNSS/readi/analysis/spectra/'
plot_dir='/home/dmelgarm/RTGNSS/plots/ppsd/'
net='RK'
exchange='READI'
day_of_year=285
###############################################################################



################        What do you want to do?    ############################

run_ppsd=False
plot_ppsd=True

#################     done with pre-amble stuff    ############################


#read stations
stations=genfromtxt(site_list,usecols=0,dtype='U')


# Make the ppsd for all sites. the logic will be as follows. Loop over the sites,
# for a particular site for a particular day, try to open the mseed file. If it
# doesn't exist, move on. If it does then try to open the ppsd object. If it
# doesn't exist, create it, and add to it. If it exists, check the times, if 
# this trace is new then add it. At the end save the new ppsd objects 
if run_ppsd:
    
    #spoof the instrument response
    paz = {'gain': 1,'poles': [1],'sensitivity': 1,'zeros': [0j, 0j]}
    
    #get station information
    stations=genfromtxt(site_list,usecols=0,dtype='U')
    
    #get available data folders
    folders=glob(mseed_dir+'/*/')
    
    #loop over sites
    for ksta in range(len(stations)):
        
        # get current station
        site=stations[ksta]
        
        #This guy keeps track of whether we've checked for ppsd initalization
        #for a particular station
        ppsd_init=False
        
        #This guy tracks whether any new ppsd data was found
        updated_ppsd=False
        
        #Keep track of whether we ever found any data whatsoever for a particular site
        data_found=False
        
        for kday in range(len(folders)):
            
            #Where are the data
            efile=folders[kday]+'/'+site+'.LXE.mseed'
            nfile=folders[kday]+'/'+site+'.LXN.mseed'
            zfile=folders[kday]+'/'+site+'.LXZ.mseed'
            
            #Check if there is data
            if exists(efile)==True:
                
                #Update boolean that checks whether data was found
                data_found=True
            
                #First read the mseed file, we will need this for creating the PPSD in
                #case it doesn;t yet exist
                e=read(efile)
                n=read(nfile)
                z=read(zfile)
                
                #on the first time that data is found, check if the PPSD exists,
                #if not then create it
                if ppsd_init==False:   #i.e. haven't checked for existence of ppsd
                
                    Eppsd_file=ppsd_dir+site+'.LXE.ppsd.npz'
                    Nppsd_file=ppsd_dir+site+'.LXN.ppsd.npz'
                    Zppsd_file=ppsd_dir+site+'.LXZ.ppsd.npz'
                
                    #Does the ppsd object exist?
                    if exists(Eppsd_file)==True:
                        
                        #Load the previously saved PPSDs
                        Eppsd = PPSD.load_npz(Eppsd_file,metadata=paz)
                        Nppsd = PPSD.load_npz(Nppsd_file,metadata=paz)
                        Zppsd = PPSD.load_npz(Zppsd_file,metadata=paz)
                        
                    #They don't exist yet, create new objects
                    else:
                        Eppsd=PPSD(e[0].stats,paz,db_bins=(-80, 20, 1.0),period_limits=[2,1200], special_handling="ringlaser")
                        Nppsd=PPSD(n[0].stats,paz,db_bins=(-80, 20, 1.0),period_limits=[2,1200], special_handling="ringlaser")
                        Zppsd=PPSD(z[0].stats,paz,db_bins=(-80, 20, 1.0),period_limits=[2,1200], special_handling="ringlaser")
                        
                    #Done, update variable
                    ppsd_init=True
                        
                #Now check if the start time of the current trace is already in the 
                #object, if it is not, tne add the trace, otherwise skip
                if Eppsd._PPSD__check_time_present(e[0].stats.starttime) == False:
                    
                    #Did you find some new data?
                    updated_ppsd=True
                    
                    #process the traces to zero out gaps
                    e=analysis.prepare_for_ppsd(e)
                    n=analysis.prepare_for_ppsd(n)
                    z=analysis.prepare_for_ppsd(z)
                    
                    Eppsd.add(e)
                    Nppsd.add(n)
                    Zppsd.add(z)
                    
        #Done with that site, save the god danged ppsd
        if updated_ppsd==True:
            print('Updating PPSd for station '+site)
            Eppsd.save_npz(Eppsd_file)
            Nppsd.save_npz(Nppsd_file)
            Zppsd.save_npz(Zppsd_file)
        else:
            print('PPSD for station '+site+' was unchanged')
            
            
            
# Now plot each one           
if plot_ppsd:
    
    #Reset any stray figures
    plt.close("all")
    
    #get station information
    stations=genfromtxt(site_list,usecols=0,dtype='U')
    
    for ksta in range(len(stations)):
        
        print('Creating plot for station '+site)
        
        #Current station
        site=stations[ksta]
    
        Eppsd_file=ppsd_dir+site+'.LXE.ppsd.npz'
        Nppsd_file=ppsd_dir+site+'.LXN.ppsd.npz'
        Zppsd_file=ppsd_dir+site+'.LXZ.ppsd.npz'
    
        #Does the ppsd object exist?
        if exists(Eppsd_file)==True:
            
            #Load the previously saved PPSDs
            Eppsd = PPSD.load_npz(Eppsd_file,metadata=paz)
            Nppsd = PPSD.load_npz(Nppsd_file,metadata=paz)
            Zppsd = PPSD.load_npz(Zppsd_file,metadata=paz)
            
            #Make ppsd plots, one per channel
            Eppsd.plot(period_lim=(2, 600),cmap=pqlx)
            ax=plt.figure(1).axes[0]
            plt.sca(ax)
            
            #Set reference lines
            plt.plot([2,600],[-11,-11],'k')
            plt.plot([2,600],[-17,-17],'k')
            plt.plot([2,600],[-23,-23],'k')
            plt.plot([2,600],[-37,-37],'k')
            plt.plot([2,600],[-57,-57],'k')
            
            bbox = dict(boxstyle="round", fc="0.8")
            ax.annotate('20cm',xy=(2.3,-11),bbox=bbox)
            ax.annotate('10cm',xy=(2.3,-18),bbox=bbox)
            ax.annotate('5cm',xy=(2.3,-25),bbox=bbox)
            ax.annotate('1cm',xy=(2.3,-38),bbox=bbox)
            ax.annotate('0.1cm',xy=(2.3,-58),bbox=bbox)
            
            plt.savefig(plot_dir+net+'.'+site+'.LXE.ppsd.png')
            plt.close()
            
            
            
            #NORTH
            
            Nppsd.plot(period_lim=(2, 600),cmap=pqlx)
            ax=plt.figure(1).axes[0]
            plt.sca(ax)
            
            #Set reference lines
            plt.plot([2,600],[-11,-11],'k')
            plt.plot([2,600],[-17,-17],'k')
            plt.plot([2,600],[-23,-23],'k')
            plt.plot([2,600],[-37,-37],'k')
            plt.plot([2,600],[-57,-57],'k')
            
            bbox = dict(boxstyle="round", fc="0.8")
            ax.annotate('20cm',xy=(2.3,-11),bbox=bbox)
            ax.annotate('10cm',xy=(2.3,-18),bbox=bbox)
            ax.annotate('5cm',xy=(2.3,-25),bbox=bbox)
            ax.annotate('1cm',xy=(2.3,-38),bbox=bbox)
            ax.annotate('0.1cm',xy=(2.3,-58),bbox=bbox)
            
            plt.savefig(plot_dir+net+'.'+site+'.LXN.ppsd.png')
            plt.close()
            
            
            #VERTICAL
            
            Zppsd.plot(period_lim=(2, 600),cmap=pqlx)
            ax=plt.figure(1).axes[0]
            plt.sca(ax)
            
            #Set reference lines
            plt.plot([2,600],[-11,-11],'k')
            plt.plot([2,600],[-17,-17],'k')
            plt.plot([2,600],[-23,-23],'k')
            plt.plot([2,600],[-37,-37],'k')
            plt.plot([2,600],[-57,-57],'k')
            
            bbox = dict(boxstyle="round", fc="0.8")
            ax.annotate('20cm',xy=(2.3,-11),bbox=bbox)
            ax.annotate('10cm',xy=(2.3,-18),bbox=bbox)
            ax.annotate('5cm',xy=(2.3,-25),bbox=bbox)
            ax.annotate('1cm',xy=(2.3,-38),bbox=bbox)
            ax.annotate('0.1cm',xy=(2.3,-58),bbox=bbox)
            
            plt.savefig(plot_dir+net+'.'+site+'.LXZ.ppsd.png')
            plt.close()