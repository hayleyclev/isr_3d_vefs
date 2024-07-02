#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 13:04:59 2024

@author: clevenger
"""

import viresclient
from viresclient import SwarmRequest
import numpy as np
import ppigrf
import lompe

"""
Parameters In: 
    - Swarm token (must enter manually every time)
    - start time (given at top level)
    - end time (given at top level)
    - time step (given at top level)
    
Parameters Out:
    - Lompe model object for Swarm C magnetometer data (gets used in pfrr_run_lompe.py)
    
"""

def collect_data(start_time, end_time, time_step):
    # Create viresclient request for Swarm C
    viresclient.set_token()
    prime = "SW_OPER_MAGC_HR_1B" # hard coding in which satellite from constellation - "MAGx"
    
    # Initialize Swarm magnetometer data array
    swarm_c_mag_data = []
    
    # Download data with viresclient 
    request = SwarmRequest()
    request.set_collection(prime)
    request.set_products(
        measurements=["B_NEC"],
        models=["CHAOS"], # here is it just CHAOS and not CHAOS-full
    )
    
    swarm_c_mag_data_request = request.get_between(start_time, end_time)
    df = swarm_c_mag_data_request.as_dataframe()

    # Check if dataframe is empty or missing columns
    if df.empty or 'B_NEC' not in df.columns or 'B_NEC_CHAOS' not in df.columns:
        print("No valid data available for the given time range.")
        return None

    # Print statements to show what is actually being pulled from Swarm request
    print("Data frame head:\n", df.head()) # helpful to see as script is running (which satellite? how long until done?)
    print("Columns in data frame:", df.columns) # troubleshooting
    print("Shape of data frame:", df.shape) # troubleshooting

    current_time = start_time

    while current_time <= end_time:
        next_time = current_time + time_step

        # Filter the data for the current "chunk" of time segmented by time_step
        chunk_df = df[(df.index >= current_time) & (df.index < next_time)]

        # Skip where Swarm is down/off/not collecting
        if chunk_df.empty:
            current_time = next_time
            continue

        # Transfornmations and calculations to get components of B
        dB = np.vstack(chunk_df.B_NEC.values - chunk_df.B_NEC_CHAOS.values)
        gdlat, height, Bn, Bu = ppigrf.ppigrf.geoc2geod(90 - chunk_df.Latitude.values, chunk_df.Radius.values * 1e-3, -dB[:, 0], -dB[:, 2])

        # Get SEGMENTED components of B for each given "chunk" of time
        chunk_df['Bn'], chunk_df['Be'], chunk_df['Bu'] = Bn, dB.T[1], Bu
        
        dB_chunk = np.vstack((chunk_df.Be.values, chunk_df.Bn.values, chunk_df.Bu.values))
        coords_chunk = np.vstack((chunk_df.Longitude.values, chunk_df.Latitude.values, (6371.2 + height) * 1e3))
        
        swarm_c_mag_data.append(lompe.Data(values=dB_chunk * 1e-9, coordinates=coords_chunk, datatype='space_mag_full', iweight=1.0))

        current_time = next_time
        

    # Returns the segmented, sorted, and appended data as a lompe model object
    return swarm_c_mag_data