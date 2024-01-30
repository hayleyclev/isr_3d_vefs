#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 12:11:07 2023

@author: clevenger
"""

import numpy as np
import pandas as pd
from datetime import timedelta
from lompe.utils.conductance import hardy_EUV
import apexpy
import lompe
import matplotlib.pyplot as plt
import h5py
from lompe.utils.save_load_utils import save_model
#import csv
plt.ioff()


# This script is a broken up into two functions - the run script for these functions is pfisr_example.py, 
# though the two functions can obviously be used for other run scripts.

# Function 1 - run_lompe_pfisr takes a pfisr data set with poker mag data and runs it through the Lompe model
def run_lompe_pfisr(start_time, end_time, freq, time_step, Kp, x_resolution, y_resolution, pfisrfn,
                    plot_save_outdir, nc_save_outdir, pokermagfn):


    # Timing - a start time and end time are given in the run script
    times = pd.date_range(start_time, end_time, freq=freq)
    # Timing - the time step is given in the run script
    DT = timedelta(seconds = time_step) # will select data from +- DT

    # Apex coordinates are used to find the magnetic eastward direction in quasi-dipole coords
    apex = apexpy.Apex(times[0], refh = 110)

    # Gridding - a resolution and region of interest are defined - this is currently set up over PFISR
    position = (-147, 65) # lon, lat
    orientation = (-1, 2) # east, north
    L, W, Lres, Wres = 500e3, 500e3, x_resolution, y_resolution # dimensions and resolution of grid
    grid = lompe.cs.CSgrid(lompe.cs.CSprojection(position, orientation), L, W, Lres, Wres, R = 6481.2e3)

    # Data set - a PFISR h5 filepath is given in the run script, and the data is extracted here
    with h5py.File(pfisrfn,"r") as h5:
        # Note: O+ indexing - error could come about if -1 used instead of 0
        
        # Beam codes - the beam codes used may be printed, but that is suppressed for now
        # beam_codes = h5['BeamCodes'][:,0]
        # print(beam_codes[:,0])
   
        # Identifying line of site velocity data points
        Vlos = h5['FittedParams/Fits'][:,:,:,0,3]
        # Filtering out any unreasonable, unrealistic, or overly noisy measurements
        Vlos[np.abs(Vlos)>1000.] = np.nan
        
        # Identifying geographic latitude, longitude, and altitude data points
        glat = h5['Geomag/Latitude'][:]
        glon = h5['Geomag/Longitude'][:]
        galt = h5['Geomag/Altitude'][:]
        
        # Identifying timing points
        utime = h5['Time/UnixTime'][:]
        # Averaging the UnixTime values along each row from the original h5 dataset
        Midtime = np.mean(utime, axis=1) # midpoint/average time for each row in dataset
    
        # Identifying directional components
        ke = h5['Geomag/ke'][:] # eastward (E-W) pointing
        kn = h5['Geomag/kn'][:] # northward (N-S) pointing
        kz = h5['Geomag/kz'][:] # upward (towards-away, to-from radar) pointing
        


    # Using Hardy Conductance model - calculating the Hall and Pederson currents
    SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, times[0], 'hall'    )
    print("lat shape: ", grid.lat.shape)
    print("lon shape: ", grid.lon.shape)
    SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, times[0], 'pedersen')
    model = lompe.Emodel(grid, Hall_Pedersen_conductance = (SH, SP))

    # This loop goes through each time and produces plots and NetCDF files at each time step
    for t in times[:]:
        print("t: ",t)
    
        # Update the Hardy Conductance model with the current time
        SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, t, 'hall'    ) # Hall current
        SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, t, 'pedersen') # Pederson current

        # Reset model with updated conductance functions
        model.clear_model(Hall_Pedersen_conductance = (SH, SP)) # reset
    
        # Calling Function 2 - prepares PFISR and poker mag data for the current time "chunk"
        pfisr_data, pokermag_data = prepare_data(ke, kn, kz, Vlos, glat, glon, galt, Midtime, t, t + DT, pokermagfn)
    
        # Add PFISR and poker mag data for current time chunk
        model.add_data(pfisr_data, pokermag_data)

        # Run the inversion using regularization parameters 
        gtg, ltl = model.run_inversion(l1 = 2, l2 = 0.1)
    
        # Save model plots
        savefile = plot_save_outdir + str(t).replace(' ','_').replace(':','')
        lompe.lompeplot(model, include_data = True, time = t, apex = apex, savekw = {'fname': savefile, 'dpi' : 200})

        # Save model output at NetCDF file
        savefile = nc_save_outdir + str(t).replace(' ','_').replace(':','')+'.nc' # create directory to save output as nc to read in
        save_model(model, file_name=savefile) # one file per time stamp




# Function 2 - prepare_data takes the PFISR h5 experiment data + poker mag csv data and reshapes it to fit into the Lompe model
def prepare_data(ke, kn, kz, Vlos, glat, glon, galt, Midtime, t0, t1, pokermagfn):
    """ get data from correct time period """

    # Find time index corresponding to the specified time range
    Tidx1_pfisr = np.argmin(np.abs(Midtime[:] - t0.timestamp())) 
    Tidx2_pfisr = np.argmin(np.abs(Midtime[:] - t1.timestamp()))
    
    # Display timing information
    print("Tidx1 (PFISR): ", Tidx1_pfisr) 
    print(t0, pd.to_datetime(Midtime[Tidx1_pfisr], unit='s'))
    print("Tidx2 (PFISR): ", Tidx2_pfisr)
    print(t1, pd.to_datetime(Midtime[Tidx2_pfisr], unit='s'))

    # Extract Vlos data within specified time range
    vlos_input = Vlos[Tidx1_pfisr:Tidx2_pfisr, :, :] 
    print("vlos input shape: ",vlos_input.shape)
    print('Vlos: ', Vlos[Tidx1_pfisr:Tidx2_pfisr, :, :].shape) 
    
    # Expand latitude and longitude arrays to match the shape of vlos_input
    glat_new = np.tile(glat, (Tidx2_pfisr - Tidx1_pfisr, 1, 1))
    glon_new = np.tile(glon, (Tidx2_pfisr - Tidx1_pfisr, 1, 1)) 
    
    # Display latitude and longitude shape information
    print("glat shape: ", glat.shape)
    print("glat (tile'd) shape:" , glat_new.shape)
    print("glon shape: ", glon.shape)
    print("glon (tile'd) shape:" , glon_new.shape)
    
    # Combine latitude and longitude arrays into a coordinate array
    coords = np.array([glon_new.flatten(), glat_new.flatten()])
    print("coords shape: ", coords.shape)
    
    # Calculate cosine of the angle between the line-of-sight and b-field
    cos_theta_input = (np.sqrt(ke**2+kn**2)/(np.sqrt(ke**2+kn**2+kz**2)))
    print('cos theta shape: ',cos_theta_input.shape)
    
    # Calculate the line-of-sight velocity and flatten it
    vlos=(vlos_input/cos_theta_input).flatten()
    # Remove any field-aligned beams
    vlos[np.abs(vlos)>5000.] = np.nan 

    # Display line-of-sight velocity array
    print("vlos shape: ",vlos.shape)

    # Normalize the magnetic field components
    ke_norm = ke/np.sqrt(ke**2+kn**2)
    kn_norm = kn/np.sqrt(ke**2+kn**2)
    
    # Expand normalized b-field components to match the shape of vlos_input
    ke_norm_new = np.tile(ke_norm, (Tidx2_pfisr - Tidx1_pfisr, 1, 1)) 
    kn_norm_new = np.tile(kn_norm, (Tidx2_pfisr - Tidx1_pfisr, 1, 1)) 
    
    # Display shapes of normalized b-field components
    print("ke_norm shape: ", ke_norm.shape)
    print("kn_norm shape: ", kn_norm.shape)
    print("ke_norm shape: ", ke_norm_new.shape)
    print("kn_norm shape: ", kn_norm_new.shape)
    
    # Combine normalized b-field components into a line-of-sight array
    los = np.array([ke_norm_new.flatten(), kn_norm_new.flatten()])
    
    # Display line-of-sight array shape
    print("los shape: ",los.shape)
    
    # Create a Lompe data object with the prepared data
    pfisr_data = lompe.Data(vlos, coordinates = coords, LOS = los, datatype = 'convection', scale = None, iweight=0.0)
    
##########################################################################################################################################
    # Set lat and lon of physical location of mag(s)
    mag_lat = 68 # estimated
    mag_lon = -150 # estimated

    # Read in mag data
    mag_data = pd.read_csv(pokermagfn)
    #mag_data['time'] = pd.to_datetime(mag_data['time_hhmmss'], format='%H:%M:%S') # Starting with time, this will need to be re-indexed
    mag_data['time'] = pd.to_datetime('2017-06-16 ' + mag_data['time_hhmmss']) # Starting with datetime object (pulled from csv)
    mag_data['unix_time'] = (mag_data['time'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s') # Converting to unix time
    
    
    # Find magnetometer data that falls within the current ISR data chunk time range
    t0_unix = t0.timestamp()
    t1_unix = t1.timestamp()
    
    # Pull mag data from desired time range in unix time
    mag_data_DT = mag_data[(mag_data['unix_time'] >= t0_unix) & (mag_data['unix_time'] < t1_unix)]
    
    
    #Midtime_mag = np.mean(mag_data['time']) # midpoint/average time for each row in dataset
    #mag_data['time'] = Midtime_mag
    
    # Create magnetic field object
    B = mag_data_DT[['H_mag_comp', 'D_mag_comp', 'Z_mag_comp']].values.T * 1e-9 # Convert to Tesla from nanotesla
    print("B Shape: ", B.shape) # should be (3, N)
    
    # Create coordinates array for the magnetometer data
    coords_mag = np.array([[mag_lon]*len(mag_data_DT), [mag_lat]*len(mag_data_DT)]) # Duplicate lon and lat for each time point
    print("Mag Coords Shape: ", coords_mag.shape) # Should be (2, N)
   
    
    # Create Lompe data object for the magnetometer data
    pokermag_data = lompe.Data(B, coords_mag, datatype='ground_mag', error=10e-9, iweight=1.0)
##########################################################################################################################################

    # Read magnetometer data
    #mag_data = pd.read_csv(pokermagfn)
    #mag_data['time'] = pd.to_datetime(mag_data['time_hhmmss'], format='%H:%M:%S')
    
    # Select data within the time chunk
    #mag_data_period = mag_data[(mag_data['time'] >= t0) & (mag_data['time'] < t1)]
    
    # If no data is found for the time period, return None or handle accordingly
    #if mag_data_period.empty:
        #print(f"No magnetometer data found for period: {t0} to {t1}")
        #return None, None
    
    # Average the magnetic field components over the time chunk
    #avg_B = mag_data_period[['H_mag_comp', 'D_mag_comp', 'Z_mag_comp']].mean().values * 1e-9
    
    # Create B array with averaged values
    # Repeat the averaged values for each time point in the period
    #B = np.tile(avg_B, (len(mag_data_period), 1)).T
    
    # Set lat and lon of the physical location of the magnetometer
    #mag_lat = 70  # Estimated latitude
    #mag_lon = -150  # Estimated longitude
    
    # Create coordinates array for the magnetometer data
    #coords_mag = np.array([[mag_lon], [mag_lat]])  # Static coordinates for the magnetometer
    
    # Create Lompe data object for the magnetometer data
    #pokermag_data = lompe.Data(B, coords_mag, datatype='ground_mag', error=10e-9, iweight=0.4)    

    

    # Return the prepared data
    return pfisr_data, pokermag_data


