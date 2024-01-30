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


def collect_data(pokermagfn, time_intervals):
    # Set lat and lon of physical location of mag(s)
    mag_lat = 68 # estimated
    mag_lon = -150 # estimated

    # Read in mag data
    mag_data = pd.read_csv(pokermagfn)
    #mag_data['time'] = pd.to_datetime(mag_data['time_hhmmss'], format='%H:%M:%S') # Starting with time, this will need to be re-indexed
    #mag_data['time'] = pd.to_datetime('2017-06-16 ' + mag_data['time_hhmmss']) # Starting with datetime object (pulled from csv)
    #### From LL: SuperMAG time stamping appears different??? ####
    mag_data['time'] = pd.to_datetime(mag_data['Date_UTC']) # Starting with datetime object (pulled from csv)
    mag_data['unix_time'] = (mag_data['time'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s') # Converting to unix time
    
    pokermag_data = list()

    for i, row in time_intervals.iterrows():
        t0 = row['starttime']
        t1 = row['endtime']

        # Find magnetometer data that falls within the current ISR data chunk time range
        t0_unix = t0.timestamp()
        t1_unix = t1.timestamp()
        
        # Pull mag data from desired time range in unix time
        mag_data_DT = mag_data[(mag_data['unix_time'] >= t0_unix) & (mag_data['unix_time'] < t1_unix)]
        
        
        #Midtime_mag = np.mean(mag_data['time']) # midpoint/average time for each row in dataset
        #mag_data['time'] = Midtime_mag
        
        # Create magnetic field object
        #B = mag_data_DT[['H_mag_comp', 'D_mag_comp', 'Z_mag_comp']].values.T * 1e-9 # Convert to Tesla from nanotesla
        ### LL - mock array formation due to different file coordinates??? NOT CORRECT!!! ###
        B = mag_data_DT[['dbe_nez', 'dbn_nez', 'dbz_nez']].values.T * 1e-9 # Convert to Tesla from nanotesla
        print("B Shape: ", B.shape) # should be (3, N)
        
        # Create coordinates array for the magnetometer data
        coords_mag = np.array([[mag_lon]*len(mag_data_DT), [mag_lat]*len(mag_data_DT)]) # Duplicate lon and lat for each time point
        print("Mag Coords Shape: ", coords_mag.shape) # Should be (2, N)
       
        
        # Create Lompe data object for the magnetometer data
        pokermag_data.append(lompe.Data(B, coords_mag, datatype='ground_mag', error=10e-9, iweight=1.0))
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
    return pokermag_data


