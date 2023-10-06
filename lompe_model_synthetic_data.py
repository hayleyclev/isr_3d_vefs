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
#from lompe.model.visualization import *
#from scipy.interpolate import griddata
plt.ioff()

conductance_functions = True

savepath = '/Users/clevenger/Projects/pfisr_synth_data/lompe_synth_outputs/' # edit to match the path you want as your outdir
pfisrfn = '/Users/clevenger/Projects/pfisr_synth_data/synthetic_data.h5' # edit to match the path where synthetic data is stored

# times during entire day
times = pd.date_range('2016-09-13 00:00', '2016-09-13 00:29', freq = '1Min') # 
# DT currently doesn't matter - only selecting 1 timestamp based on t0
DT = timedelta(seconds = 2 * 60) # will select data from +- DT

apex = apexpy.Apex(times[0], refh = 110) # set parameter for Apex model

Kp = 1 # for Hardy conductance model - manually set, but up to user as this is synthetic and not attached to a real event

# set up grid
position = (-147, 65) # lon, lat - currently set over approximate center of PFISR
orientation = (-1, 2) # east, north
L, W, Lres, Wres = 500e3, 500e3, 50.e3, 50.e3 # dimensions and resolution of grid
grid = lompe.cs.CSgrid(lompe.cs.CSprojection(position, orientation), L, W, Lres, Wres, R = 6481.2e3) # grid formed by input parameters

with h5py.File(pfisrfn,"r") as h5: # read out data from synthetic data h5 file
    
    Vlos = h5['FittedParams/Fits'][:,:,:,0,3] # Vlos fields from h5
    #Vlos_max_nonan = np.nanmax(Vlos) # determining the max Vlos value that is not NaN
    #Vlos[np.isnan(Vlos)] = Vlos_max_nonan # masking the NaNs with the max real value of Vlos
    #Vlos_list1 = Vlos # assigning a name to the array to print
    #print("Check Vlos for nans: ", Vlos_list1) # printing the array, check for NaNs
    #Vlos_list2 = Vlos[np.isnan(Vlos)] # creating an array of all NaNs
    # print("Vlos nans: ", Vlos_list2) # printing array of all NaNs (SHOULD BE EMPTY!)
    # print("Vlos input shape: ", Vlos.shape)
    # print("Vlos used for calculations: ", Vlos)
    Vlos[np.abs(Vlos)>1000.] = np.nan
    
    glat = h5['Geomag/Latitude'][:] # glat fields from h5
    # glat_max_nonan = np.nanmax(glat) # determining the max glat value that is not NaN
    # glat[np.isnan(glat)] = glat_max_nonan # masking the NaNs with the max real value of glat
    # glat_list1 = glat # assigning a name to the array to print
    # print("Check glat for nans: ", glat_list1) # printing the array, check for NaNs
    # glat_list2 = glat[np.isnan(glat)] # creating an array of all NaNs
    # print("glat nans: ", glat_list2) # printing array of all NaNs (SHOULD BE EMPTY!)
    
    glon = h5['Geomag/Longitude'][:] # glon fields from h5
    # glon_max_nonan = np.nanmax(glon) # determining the max glon value that is not NaN
    # glon[np.isnan(glon)] = glon_max_nonan # masking the NaNs with the max real value of glon
    # glon_list1 = glon # assigning a name to the array to print
    # print("Check glon for nans: ", glon_list1) # printing the array, check for NaNs
    # glon_list2 = glon[np.isnan(glon)] # creating an array of all NaNs
    # print("glon nans: ", glon_list2) # printing array of all NaNs (SHOULD BE EMPTY!)
    
    galt = h5['Geomag/Altitude'][:] # galt fields from h5
    # galt_max_nonan = np.nanmax(galt) # determining the max galt value that is not NaN
    # galt[np.isnan(galt)] = galt_max_nonan # masking the NaNs with the max real value of galt
    # galt_list1 = galt # assigning a name to the array to print
    # print("Check galt for nans: ", galt_list1) # printing the array, check for NaNs
    # galt_list2 = galt[np.isnan(galt)] # creating an array of all NaNs
    # print("galt nans: ", galt_list2) # printing array of all NaNs (SHOULD BE EMPTY!)
    
    utime = h5['Time/UnixTime'][:] # utime fields from h5
    # utime_max_nonan = np.nanmax(utime) # determining the max utime value that is not NaN
    # utime[np.isnan(utime)] = utime_max_nonan # masking the NaNs with the max real value of utime
    # utime_list1 = utime # assigning a name to the array to print
    # print("Check utime for nans: ", utime_list1) # printing the array, check for NaNs
    # utime_list2 = utime[np.isnan(utime)] # creating an array of all NaNs
    # print("utime nans: ", utime_list2) # printing array of all NaNs (SHOULD BE EMPTY!)
    
    ke = h5['Geomag/ke'][:] # ke fields from h5
    # ke_max_nonan = np.nanmax(ke) # determining the max ke value that is not NaN
    # ke[np.isnan(ke)] = ke_max_nonan # masking the NaNs with the max real value of ke
    # ke_list1 = ke # assigning a name to the array to print
    # print("Check ke for nans: ", ke_list1) # printing the array, check for NaNs
    # ke_list2 = ke[np.isnan(ke)] # creating an array of all NaNs
    # print("ke nans: ", ke_list2) # printing array of all NaNs (SHOULD BE EMPTY!)
    # print("ke used for calculations: ", ke)

    kn = h5['Geomag/kn'][:] # kn fields from h5
    # kn_max_nonan = np.nanmax(kn) # determining the max kn value that is not NaN
    # kn[np.isnan(kn)] = kn_max_nonan # masking the NaNs with the max real value of kn
    # kn_list1 = kn # assigning a name to the array to print
    # print("Check kn for nans: ", kn_list1) # printing the array, check for NaNs
    # kn_list2 = kn[np.isnan(kn)] # creating an array of all NaNs
    # print("kn nans: ", kn_list2) # printing array of all NaNs (SHOULD BE EMPTY!)
    # print("kn used for calculations: ", kn)
    
    kz = h5['Geomag/kz'][:] # kz fields from h5
    # kz_max_nonan = np.nanmax(kz) # determining the max ke value that is not NaN
    # kz[np.isnan(kz)] = kz_max_nonan # masking the NaNs with the max real value of kz
    # kz_list1 = kz # assigning a name to the array to print
    # print("Check kz for nans: ", kz_list1) # printing the array, check for NaNs
    # kz_list2 = kz[np.isnan(kz)] # creating an array of all NaNs
    # print("kz nans: ", kz_list2) # printing array of all NaNs (SHOULD BE EMPTY!)
    # print("kz used for calculations: ", kz)

# The above files contain entire synthetic data "experiment"
# Function to select from a smaller time interval is needed:
def prepare_data(t0, t1):
    """ get data from correct time period """

    Tidx1 = np.argmin(np.abs(utime[:,0] - t0.timestamp())) # indexing the time, choosing min time for t0
    #Tidx2 = np.argmin(np.abs(utime[:,0]- t1.timestamp())) # can use another timestamp when using DT
    #print("Tidx1: ",Tidx1) # when using both, print
    #print("Tidx2: ",Tidx2) # when using both, print

    print(t0, pd.to_datetime(utime[Tidx1,0], unit='s')) # print out experiment date
    
    coords = np.array([glon.flatten(), glat.flatten()]) # create coords attribute from lat & lon values, reshaping
    print("coords shape: ", coords.shape) # check coordinate shape to make sure it matches (2,N) structure
    
    vlos_input = Vlos[Tidx1,:,:] # taking a cut in time of Vlos
    cos_theta_input = (np.sqrt(ke**2+kn**2)/(np.sqrt(ke**2+kn**2+kz**2))) # vector math to normalize vlos
    vlos=(vlos_input/cos_theta_input).flatten() # reshaping vlos to use as model input
    vlos[np.abs(vlos)>5000.] = np.nan
    print("vlos shape: ", vlos.shape) # check vlos shape to make sure it matches (N,) structure
    print("vlos, after vector math: ", vlos)
    
    ke_norm = ke/np.sqrt(ke**2+kn**2) # vector math to normalize los
    kn_norm = kn/np.sqrt(ke**2+kn**2) # vector math to normalize los
    print("ke_norm shape: ", ke_norm.shape) # verify normalization
    print("kn_norm shape: ", kn_norm.shape) # verify normalization
    los = np.array([ke_norm.flatten(), kn_norm.flatten()]) # reshaping los to use as model input
    print("los shape: ", los.shape) # check los shape to make sure it matches (2,N) structure
    
    pfisr_data = lompe.Data(vlos, coordinates = coords, LOS = los, datatype = 'convection', scale = None) # input reshaped data into model
    
    print("prepared vlos: ", vlos)
    print("prepared los: ", los)
    
    return pfisr_data # PFISR data reshaped and ready for model incorporation


SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, times[0], 'hall'    ) # calculating Hall conductances
SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, times[0], 'pedersen') # calculating Pederson conductances
model = lompe.Emodel(grid, Hall_Pedersen_conductance = (SH, SP)) # shaping to fit set grid

# loop through times and save
for t in times[1:]:
    print("t: ",t)
    
    SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, t, 'hall'    )
    SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, t, 'pedersen')

    model.clear_model(Hall_Pedersen_conductance = (SH, SP)) # reset
    
    pfisr_data = prepare_data(t, t + DT)
    
    model.add_data(pfisr_data)

    gtg, ltl = model.run_inversion(l1 = 2, l2 = 0.1) # damping parameters - fine tune on own
    
    savefile = savepath + str(t).replace(' ','_').replace(':','')
    
    #################################################################################################
    # only uncomment the plotting process below once you're sure there are no NaNs from input data! #
    #################################################################################################
    
    lompe.lompeplot(model, include_data = True, time = t, apex = apex, savekw = {'fname': savefile, 'dpi' : 200}) # plotting!
    plt.close("all")
    
    #test
    model.v(-147.0,65.0)
    
    
    
    
    
    
    
    
    