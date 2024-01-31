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


def collect_data(supermagfn, time_intervals):


 # Read in mag data
    mag_data = pd.read_csv(supermagfn)
    #mag_data['time'] = pd.to_datetime(mag_data['time_hhmmss'], format='%H:%M:%S') # Starting with time, this will need to be re-indexed
    mag_data['time'] = pd.to_datetime(mag_data['Date_UTC'], format='%Y-%m-%dT%H:%M:%S') # Starting with datetime object (pulled from csv)
    mag_data['unix_time'] = (mag_data['time'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s') # Converting to unix time


    supermag_data = list()

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
        #B = mag_data_DT[['dbn_nez', 'dbe_nez', 'dbz_nez']].values.T * 1e-9 # Convert to nanoesla from Tesla
        B = mag_data_DT[['dbn_nez', 'dbe_nez', 'dbz_nez']].values.T * 1e-9 # supermag given in nT, lompe needs Tesla so convert to Tesla
        #B = np.tile(B, (mag_data_DT.shape[0], 1)).T
        print("B Shape: ", B.shape) # should be (3, N)
       
        # Create coordinates array for the magnetometer data
        coords_mag = mag_data_DT[['GEOLON', 'GEOLAT']].values.T # Duplicate lon and lat for each time point
        print("Mag Coords Shape: ", coords_mag.shape) # Should be (2, N)
      
        
        # Create Lompe data object for the magnetometer data
        supermag_data.append(lompe.Data(B, coords_mag, datatype='ground_mag', error=10e-9, iweight=0.001))


    # Return the prepared data
    return supermag_data


