#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 14:52:33 2018

@author: dmelgarm
"""

def g0(self, L):
    """acceleration due to gravity at the elipsoid surface at latitude L"""
    
    from numpy import sin,sqrt
    
    g=9.7803267715 * (1 + 0.001931851353 * sin(L)**2) / \
                       sqrt(1 - 0.0066943800229 * sin(L)**2)
    return g



class WGS84:    #Semimajor axis length (m)
   
    from numpy import sqrt

    a = 6378137.0
    #Semiminor axis length (m)
    b = 6356752.3142
    #Ellipsoid flatness (unitless)
    f = (a - b) / a
    #Eccentricity (unitless)
    e = sqrt(f * (2 - f))
    #Speed of light (m/s)
    c = 299792458.
    #Relativistic constant
    F = -4.442807633e-10
    #Earth’s universal gravitational constant
    mu = 3.986005e14
    #Earth rotation rate (rad/s)
    omega_ie = 7.2921151467e-5    
   

                       
def ecef2lla(x,y,z, tolerance=1e-9):
   '''
   Convert Earth-centered, Earth-fixed coordinates to lat, lon, alt.
   Input: ecef - (x, y, z) in (m, m, m)
   Output: lla - (lat, lon, alt) in (decimal degrees, decimal degrees, m)
   '''
   
   
   from numpy import sqrt,cos,rad2deg,arctan2,arctan,zeros

   #Outut variables
   lon=zeros(len(x))
   lat=zeros(len(y))
   alt=zeros(len(z))
   
   #define ellipsoid
   ellipsoid=WGS84
   N = ellipsoid.a
    
   #loop over ever coordinate
   for k in range(len(lon)):
    
       #Calculate lon
       lon[k] = arctan2(y[k], x[k])
       p = sqrt(x[k]**2 + y[k]**2)
       tempLat=0
       previousLat = 90
       tempAlt=0
       #Iterate until tolerance is reached
       while abs(tempLat - previousLat) >= tolerance:
            previousLat = tempLat
            sinLat = z[k] / (N * (1 - ellipsoid.e**2) + tempAlt)
            tempLat = arctan((z[k] + ellipsoid.e**2 * N * sinLat) / p)
            N = ellipsoid.a / sqrt(1 - (ellipsoid.e * sinLat)**2)
            tmpAlt = p / cos(tempLat) - N
       #Done, define output
       lat[k]=tempLat
       alt[k]=tmpAlt
        
   #Return the lla coordinates
   return rad2deg(lon), rad2deg(lat), alt


def rotate2neu(x,y,z,ref_x,ref_y,ref_z,lon,lat):
   """
   Rotate from ECEF 2 local NEU, this follows equation 1 in Bock et al (2011)
   in BSSA. Given a rotation matrix R form the data vector X=(Xi-X0), where Xi
   are the per epoch observations and X0 the reference coords, all in ECEF. R is
   formed using the same reference coordinates but in lon/lat space
   """
   
   from numpy import deg2rad,sin,cos,expand_dims,array,r_
   
   lat=deg2rad(lat)
   lon=deg2rad(lon)
   R=array([[-sin(lat)*cos(lon),-sin(lon)*sin(lat),cos(lat)],[-sin(lon),cos(lon),0],[cos(lon)*cos(lat),cos(lat)*sin(lon),sin(lat)]])
   D=r_[expand_dims(x,0)-ref_x,expand_dims(y,0)-ref_y,expand_dims(z,0)-ref_z]
   C=R.dot(D)
   n=C[0]
   e=C[1]
   u=C[2]    
   return n,e,u