#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 19:53:21 2024

@author: clevenger
"""

import lompe
import numpy
import numpy as np
from viresclient import SwarmRequest
import viresclient
import datetime as dt
import ppigrf
import dipole

#savepath = '/Users/clevenger/Projects/data_assimilation/march_19/lompe_outputs/swarm/mag'

def collect_data(start_time, end_time):

    #token r-8-mlkP_RBx4mDv0di5Bzt3UZ52NGg-
    # my token: vOzoHzs61RJYFjDTizvm0TPWu6JC_WIp
    viresclient.set_token()

    prime = "SW_EXPT_EFIC_TCT02"


    #t0 = dt.datetime(2017, 6, 16, 14, 00)



    current_time = start_time
    while current_time <= end_time:
        request = SwarmRequest()
        request.set_collection(prime)
        request.set_products(
            measurements=['VsatN', 'VsatE', 'VsatC'],
            auxiliaries=['Latitude', 'Longitude', 'Radius', 'QDLat', 'QDLon', 'MLT'],
            sampling_step='PT1S'
        )
        
        # Fetch the data between start_time and end_time
        data = request.get_between(start_time, end_time)
        df = data.as_dataframe()
        
        # Calculate vlos, coords, and los for lompe.Data object
        vlos = df[['VsatN', 'VsatE', 'VsatC']].to_numpy()
        #coords = df[['QDLat', 'QDLon']].to_numpy().T  # Magnetic coordinates as location
        #coords = np.array([glon_new.flatten(), glat_new.flatten()])
        #coords = np.array([df['QDLat'].values, df['QDLon'].values])
        #coords = coords.T
        coords = np.vstack((df['Longitude'], df['Latitude'], df['Radius'])).T
        los = np.ones_like(vlos)  # Placeholder; LOS vector needs to be calculated based on the context
        

        #dB = np.vstack(df.B_NEC.values  - df.B_NEC_CHAOS.values)
        #print(df.B_NEC.values.shape)
        #print(df.B_NEC_CHAOS.values.shape)
        

        #gdlat, height, Bn, Bu = ppigrf.ppigrf.geoc2geod(90 - df.Latitude.values, df.Radius.values * 1e-3, -dB[:, 0], -dB[:, 2])
        
        # NaN out data outside the specified latitude and longitude ranges
        lat_range = (45, 75)
        lon_range = (-175, -130)
        
        # Apply range filter
        outside_range = ~df['Latitude'].between(*lat_range) | ~df['Longitude'].between(*lon_range)
        df.loc[outside_range, ['VsatN', 'VsatE', 'VsatC']] = np.nan


        # get the spacecraft velocity at t0:
        lo = df.Longitude.values * np.pi / 180
        la = df.Latitude.values * np.pi / 180

        # make N *unit* position vectors - this will be a 3 x N array with the x, y, and z coordinates in the rows
        r = np.vstack((np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)))
        r = r * df.Radius.values.reshape((1, -1)) # multiply by a row array (1, N) that contains radii to get correct lengths

        # calculate the velocity by taking the difference - here it is important that the time steps are all equal
        dr = r[:, 1:] - r[:, :-1] # delta r (one fewer vectors in dr than in r)

        v_enu = dipole.ecef_to_enu(dr.T, df.Longitude[:-1].values, df.Latitude[:-1].values).T
        v_enu = v_enu[:, v_enu.shape[1]//2]
        v_enu = v_enu / np.linalg.norm(v_enu)

        # set up the grid
        #p = cs.CSprojection((np.rad2deg(lo[lo.size//2]), np.rad2deg(la[lo.size//2])), orientation = v_enu[:2])
        #grid = cs.CSgrid(p, 2000.e3, 1000.e3, 40.e3, 50.e3, R = (6371.2 + 110) * 1e3)
        
        #model = lompe.Emodel(grid, (lambda lon, lat: conductance(lon, lat, 'h'), lambda lon, lat: conductance(lon, lat, 'p')))

        #coords = np.vstack((df['Longitude'].values, df['Latitude'].values, df['Radius'].values)).T
        swarm_c_flow_data = lompe.Data(vlos, coordinates=coords, LOS=los, datatype='convection', scale=None)
        
        #savefile = savepath + str(t0).replace(' ','_').replace(':','')
        #lompe.lompeplot(model, include_data = True, time = t0, apex = a, savekw = {'fname': savefile, 'dpi' : 200})
        
        current_time += dt.timedelta(minutes=1)
    
    
    return swarm_c_flow_data