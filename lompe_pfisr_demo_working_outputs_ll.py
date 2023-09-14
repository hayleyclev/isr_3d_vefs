# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 10:42:54 2023

@author: hzibi
"""

import numpy as np
import pandas as pd
# import datetime
from datetime import timedelta
from lompe.utils.conductance import hardy_EUV
import apexpy
import lompe
import matplotlib.pyplot as plt
import h5py
plt.ioff()


conductance_functions = True

savepath = '../demo_figures/temp_outputs'
pfisrfn = '/Users/e30737/Desktop/Data/AMISR/PFISR/2017/20170616.001_lp_1min-fitcal.h5'

# times during entire day
times = pd.date_range('2017-06-16 14:00', '2017-06-16 15:00', freq = '1Min')
# DT currently doesn't matter - only selecting 1 timestamp based on t0
DT = timedelta(seconds = 2 * 60) # will select data from +- DT

apex = apexpy.Apex(times[0], refh = 110)

Kp = 5 # for Hardy conductance model

# set up grid
position = (-147, 65) # lon, lat
orientation = (-1, 2) # east, north
L, W, Lres, Wres = 500e3, 500e3, 50.e3, 50.e3 # dimensions and resolution of grid
grid = lompe.cs.CSgrid(lompe.cs.CSprojection(position, orientation), L, W, Lres, Wres, R = 6481.2e3)

with h5py.File(pfisrfn,"r") as h5:
    Vlos = h5['FittedParams/Fits'][:,:,:,-1,3]
    glat = h5['Geomag/Latitude'][:]
    glon = h5['Geomag/Longitude'][:]
    galt = h5['Geomag/Altitude'][:]
    utime = h5['Time/UnixTime'][:]
    
    ke = h5['Geomag/ke'][:]
    kn = h5['Geomag/kn'][:]
    kz = h5['Geomag/kz'][:]

# These files contain entire AMISR experiment. Function to select from a smaller time interval is needed:
def prepare_data(t0, t1):
    """ get data from correct time period """

    Tidx1 = np.argmin(np.abs(utime[:,0] - t0.timestamp()))
    #Tidx2 = np.argmin(np.abs(utime[:,0]- t1.timestamp()))
    #print("Tidx1: ",Tidx1)
    #print("Tidx2: ",Tidx2)

    print(t0, pd.to_datetime(utime[Tidx1,0], unit='s'))
    
    print("glat shape:" ,glat.shape)
    print("glon shape:" ,glon.shape)
    coords = np.array([glon.flatten(), glat.flatten()])
    print("coords shape: ",coords.shape)
    
    vlos_input = Vlos[Tidx1,:,:]
    print("vlos input shape: ",vlos_input.shape)
    cos_theta_input = (np.sqrt(ke**2+kn**2)/(np.sqrt(ke**2+kn**2+kz**2)))
    print('cos theta shape: ',cos_theta_input.shape)
    vlos=(vlos_input/cos_theta_input).flatten()
    print("vlos shape: ",vlos.shape)
    
    ke_norm = ke/np.sqrt(ke**2+kn**2)
    kn_norm = kn/np.sqrt(ke**2+kn**2)
    print("ke_norm shape: ",ke_norm.shape)
    print("kn_norm shape: ",kn_norm.shape)
    los = np.array([ke_norm.flatten(), kn_norm.flatten()])
    print("los shape: ",los.shape)
    
    pfisr_data = lompe.Data(vlos, coordinates = coords, LOS = los, datatype = 'convection', scale = None)
    
    return pfisr_data

# get figures from entire day and save somewhere


SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, times[0], 'hall'    )
SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, times[0], 'pedersen')
model = lompe.Emodel(grid, Hall_Pedersen_conductance = (SH, SP))

# loop through times and save
for t in times[1:]:
    print("t: ",t)
    
    SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, t, 'hall'    )
    SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, t, 'pedersen')

    model.clear_model(Hall_Pedersen_conductance = (SH, SP)) # reset
    
    pfisr_data = prepare_data(t, t + DT)
    
    model.add_data(pfisr_data)

    gtg, ltl = model.run_inversion(l1 = 2, l2 = 0)
    
    savefile = savepath + str(t).replace(' ','_').replace(':','')
    lompe.lompeplot(model, include_data = True, time = t, apex = apex, savekw = {'fname': savefile, 'dpi' : 200})

