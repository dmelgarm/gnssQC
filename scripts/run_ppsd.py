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
import argparse
from os.path import exists
from glob import glob




##############     parse the command line       ###############################

parser = argparse.ArgumentParser()
parser.add_argument("--net", help="CW, SI, JP, or RK")
parser.add_argument("--exchange", help="CWU, SIO, JPL or READI")
parser.add_argument("--day_of_year", help="First day of year")
parser.add_argument("--working_dir", help="Path to mseed folders")
parser.add_argument("--ppsd_dir", help="Path to PPSD objects")
parser.add_argument("--sitelist", help="Path to station sitelist")
args = parser.parse_args()

#assign argumens to variables
net=args.net
exchange=args.exchange
site_list=args.sitelist
working_dir=args.working_dir
day_of_year=args.day_of_year

print(net)
print(exchange)
print(site_list)
print(mseed_dir)
print(ppsd_dir)
print(day_of_year)

##############       done parsing       #######################################



################        What do you want to do?    ############################

run_ppsd=True
plot_ppsd=True

#################     done with pre-amble stuff    ############################



#Find the folders with data
folders=glob(working_dir+'*')
print(folders)

#read stations
stations=genfromtxt(site_list,usecols=0,dtype='U')


# Make the ppsd for all sites. the logic will be as follows. Loop over the sites
# for a aprticular site for a aprticular day, try to open the mseed file. If it
# doesn't exist, move on. If it does then try to open the ppsd object. If it
# doesn;t exist, create it, and add to it. If it exists, check the times, if 
# this trace is new then add it. At the end save the new ppsd objects 
if run_ppsd:
    
    #spoof the instrument response
    paz = {'gain': 1,'poles': [1],'sensitivity': 1,'zeros': [0j, 0j]}
    
    #Loop over stations
    
    
    
    #Check if the ppsd object exists
    
    
