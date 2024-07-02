#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 13:58:23 2024

@author: clevenger
"""

import viresclient
from viresclient import SwarmRequest
import numpy as np
import ppigrf
import dipole
from secsy import cubedsphere as cs
import lompe

"""
Parameters In: 
    - Swarm token
    - start time (may be smaller range than total experiment)
    - end time (may be smaller range than total experiment)
    
Parameters Out:
    - Lompe model object for Swarm A magnetometer data
    
"""

def collect_data(start_time, end_time, time_step, grid):
    # Create viresclient request
    viresclient.set_token()
    prime = "SW_PREL_EFIAIDM_2_" # hard coding in which satellite from constellation - "MAGx"
    
    current_time = start_time
    swarm_a_flow_data = []

    while current_time <= end_time:
        t0 = current_time

        # download data with viresclient
        request = SwarmRequest()
        request.set_collection(prime)
        request.set_products(
            measurements=["V_i"],
            models=["CHAOS"], # here is it just CHAOS and not CHAOS-full
        )

        swarm_a_flow_data_request = request.get_between(t0 - time_step, t0 + time_step)
        
        df = swarm_a_flow_data_request.as_dataframe()

        # Print statements to show what is actually being pulled from Swarm request
        print("Data frame head:\n", df.head())
        print("Columns in data frame:", df.columns)
        print("Shape of data frame:", df.shape)

        # Check if dataframe is empty or missing columns
        if df.empty or 'V_i' not in df.columns or 'V_i_CHAOS' not in df.columns:
            print("No valid data available for the given time range.")
            current_time += time_step
            continue
        
        # get vlos
        vlos = df['V_i']
        
        # get los
        los = df['V_los']

        gdlat, height = ppigrf.ppigrf.geoc2geod(90 - df.Latitude.values, df.Radius.values * 1e-3)

        
        # NEXT STUFF ONLY FOR MOVING GRID!!!

        # get the spacecraft velocity at t0:
        #lo = df.Longitude.values * np.pi / 180 # convert to radians and from pandas.Series to numpy array
        #la = df.Latitude.values * np.pi / 180

        # make N *unit* position vectors - this will be a 3 x N array with the x, y, and z coordinates in the rows
        #r = np.vstack((np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)))
        #r = r * df.Radius.values.reshape((1, -1)) # multiply by a row array (1, N) that contains radii to get correct lengths

        # calculate the velocity by taking the difference - here it is important that the time steps are all equal
        #dr = r[:, 1:] - r[:, :-1] # delta r (one fewer vectors in dr than in r)

        #v_enu = dipole.ecef_to_enu(dr.T, df.Longitude[:-1].values, df.Latitude[:-1].values).T
        #v_enu = v_enu[:, v_enu.shape[1]//2]
        #v_enu = v_enu / np.linalg.norm(v_enu)

        # set up the grid
        #p = cs.CSprojection((np.rad2deg(lo[lo.size//2]), np.rad2deg(la[lo.size//2])), orientation = v_enu[:2])
        
        # Create rest of inputs for lompe object
        
        coords = np.vstack((df.Longitude.values, df.Latitude.values, (6371.2 + height) * 1e3))
        swarm_a_flow_data = lompe.Data(vlos, coordinates = coords, LOS = los, datatype = 'convection', scale = None)

        
        current_time += time_step

    # Return the prepared data
    return swarm_a_flow_data