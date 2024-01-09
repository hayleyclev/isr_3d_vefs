#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 10:24:01 2023

@author: clevenger
"""

import numpy as np
import pandas as pd
# import datetime
from datetime import timedelta
from lompe.utils.conductance import hardy_EUV
from lompe.utils.save_load_utils import save_model
import apexpy
import lompe
import matplotlib.pyplot as plt
import h5py
from scipy.interpolate import interp1d
plt.ioff()


conductance_functions = True

savepath = '/Users/clevenger/Projects/lompe_pfisr/test_ouputs'
pfisrfn = '/Users/clevenger/Projects/lompe_pfisr/test_datasets/20170616.001_lp_1min-fitcal.h5'

# times during entire day
times = pd.date_range('2017-06-16 14:00', '2017-06-16 14:59', freq = '1Min')
# DT currently doesn't matter - only selecting 1 timestamp based on t0
DT = timedelta(seconds = 2 * 60) # will select data from +- DT

apex = apexpy.Apex(times[0], refh = 110)

Kp = 1 # for Hardy conductance model

# set up grid
position = (-147, 65) # lon, lat
orientation = (-1, 2) # east, north
L, W, Lres, Wres = 500e3, 500e3, 50.e3, 50.e3 # dimensions and resolution of grid
grid = lompe.cs.CSgrid(lompe.cs.CSprojection(position, orientation), L, W, Lres, Wres, R = 6481.2e3)

with h5py.File(pfisrfn,"r") as h5:
    #Vlos = h5['FittedParams/Fits'][:,:,:,-1,3]
    # O+ indexing
    #beam_codes = h5['BeamCodes'][:,0]
    #print(beam_codes[:,0])
    Vlos = h5['FittedParams/Fits'][:,:,:,0,3]
    Vlos[np.abs(Vlos)>1000.] = np.nan
    
    #print("Vlos as maxes, nan'd", Vlos)
    glat = h5['Geomag/Latitude'][:]
    glon = h5['Geomag/Longitude'][:]
    galt = h5['Geomag/Altitude'][:]
    utime = h5['Time/UnixTime'][:]
    
    #print("Vlos used for calculations: ", Vlos)
    
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

    #print(t0, pd.to_datetime(utime[Tidx1,0], unit='s'))
    
    #print("glat shape:" ,glat.shape)
    #print("glon shape:" ,glon.shape)
    coords = np.array([glon.flatten(), glat.flatten()])
    #print("coords shape: ",coords.shape)
    
    vlos_input = Vlos[Tidx1,:,:]
    #print("vlos input shape: ",vlos_input.shape)
    # estimate parallel velocity here instead of finding theta - FAV=0, no LOS diff
    cos_theta_input = (np.sqrt(ke**2+kn**2)/(np.sqrt(ke**2+kn**2+kz**2)))
    #print('cos theta shape: ',cos_theta_input.shape)
    vlos=(vlos_input/cos_theta_input).flatten()
    vlos[np.abs(vlos)>5000.] = np.nan #quick fix for vertical, FA beams
    # beam filtering - scaling vertical components - uncertainties
    #print("vlos shape: ",vlos.shape)
    #print("vlos used for calculations: ", vlos)
    
    ke_norm = ke/np.sqrt(ke**2+kn**2)
    kn_norm = kn/np.sqrt(ke**2+kn**2)
    #print("ke_norm shape: ",ke_norm.shape)
    #print("kn_norm shape: ",kn_norm.shape)
    los = np.array([ke_norm.flatten(), kn_norm.flatten()])
    #print("los shape: ",los.shape)
    
    pfisr_data = lompe.Data(vlos, coordinates = coords, LOS = los, datatype = 'convection', scale = None)
    
    #print("prepared vlos: ", vlos)
    #print("prepared los: ", los)
    
    return pfisr_data

# get figures from entire day and save somewhere


SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, times[0], 'hall'    )
SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, times[0], 'pedersen')
model = lompe.Emodel(grid, Hall_Pedersen_conductance = (SH, SP))


#set up to store values for convection velocities
ve_array = []
vn_array = []
alt_array = []
#vu_array = []

# loop through times and save
for t in times[1:]:
    print("t: ",t)
    
    SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, t, 'hall'    )
    SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, t, 'pedersen')

    model.clear_model(Hall_Pedersen_conductance = (SH, SP)) # reset
    
    pfisr_data = prepare_data(t, t + DT)
    
    model.add_data(pfisr_data)

    gtg, ltl = model.run_inversion(l1 = 2, l2 = 0.1)
    
    
    
    #vvels_fn='/Users/clevenger/Projects/lompe_pfisr/vvels_in/20170616.001_lp_1min-fitcal-vvels_lat.h5'
    #vvels_in=pickle.dump(model, vvels_fn)
    
    savefile = savepath + str(t).replace(' ','_').replace(':','')
    #lompe.lompeplot(model, include_data = True, time = t, apex = apex, savekw = {'fname': savefile, 'dpi' : 200})


    
    #ve_vec.append(ve)
    #vn_vec.append(vn)
    #print("ve vec: ", ve_vec) 
    #print("vn vec: ", vn_vec) 
    
    #print(ve_vec.shape)
    #print(vn_vec.shape)
    
    # write to create new with each iteration - no overwriting
    
    
# timing?? - will need to time stamp - throw back into loop and keep time stamps for each iteration    
for t in times[1:]:  #in same minute-interval chunks - how to get to there?
    print("timestamp: ", t)
    for alt in galt[1:]:
        #ve, vn = model.v(-147, 65) # lon, lat
        ve, vn = model.v() # lon, lat
        #ve_array.append(ve)
        #vn_array.append(vn)
        print("ve: ", ve) 
        print("vn: ", vn) 
        print("ve shape: ", ve.shape)
        print("vn shape: ", vn.shape)
    
    #vu_alt = galt.flatten() # take altitude data for vu
    #alt_array.append(vu_alt) # make altitude array for matrix math to find vu
    #kz_array = kz.flatten()
    #vu_array = 
    #print("vu shape: ", vu_array.shape)
    
    savefile = f'/Users/clevenger/Projects/lompe_pfisr/lompe_output_xarray_{str(t).replace(" ","_").replace(":","")}.nc' # create directory to save output as nc to read in
    save_model(model, file_name=savefile) # one file per time stamp
    
    
#for i, t in enumerate(times[1:]):
 #   print("timestamp: ", t)
 #   print("ve: ", ve_array[i])
 #   print("vn: ", vn_array[i])
    
    
#ve_array = np.array() #take each value of ve from previous loop
#vn_array = np.array() # take each value of vn from previous loop
#alt_array = np.array() # take altitudes from hdf5 file
#vu_array = np.array(alt_array) # determine scaling factor that makes sense

#vel_array = np.stack((ve_array, vn_array, vu_array), axis=-1) # combine data into same array shape as PFISR data
#print(vel_array) # sanity check
    
    
    
    






#file='/Users/clevenger/Projects/lompe_pfisr/lompe_output_xarray_test/'
#save_path = save_model(model, file_name=file)
    
    