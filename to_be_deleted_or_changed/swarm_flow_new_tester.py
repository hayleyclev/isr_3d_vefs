#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 22:42:35 2024

@author: clevenger
"""

import lompe
import numpy
import numpy as np
from viresclient import SwarmRequest
import viresclient
from secsy import cubedsphere as cs
import datetime as dt
import pandas as pd
import apexpy
import ppigrf
import dipole
import matplotlib.pyplot as plt

#savepath = '/Users/clevenger/Projects/data_assimilation/march_19/lompe_outputs/swarm/mag'

def collect_data(start_time, end_time):

    #token r-8-mlkP_RBx4mDv0di5Bzt3UZ52NGg-
    # my token: vOzoHzs61RJYFjDTizvm0TPWu6JC_WIp
    viresclient.set_token()

    prime = "SW_EXPT_EFIA_TCT02"

    DT = dt.timedelta(seconds = 5 * 60)


    #t0 = dt.datetime(2017, 6, 16, 14, 00)



    current_time = start_time
    while current_time <= end_time:
        t0 = current_time
        a = apexpy.Apex(t0)

        # download data with Vireclien
        request = SwarmRequest()
        request.set_collection(prime)
        request.set_products(
            measurements=["VsatC","VsatE","VsatN", "Vicrx", "Vicry", "Vicrz",
                          "Vixv", "Vixh", "Viy", "Viz", "Latitude_QD", "MLT_QD"],
            models=["CHAOS"], # here is it just CHAOS and not CHAOS-full
            )

        data = request.get_between(t0 - DT, t0 + DT)

        df = data.as_dataframe()
        
        print(df.columns)

        dB = np.vstack(df.B_NEC.values  - df.B_NEC_CHAOS.values)
        print(df.B_NEC.values.shape)
        print(df.B_NEC_CHAOS.values.shape)
        

        gdlat, height= ppigrf.ppigrf.geoc2geod(90 - df.Latitude.values, df.Radius.values * 1e-3)
        
        
        # NaN out data outside the specified latitude and longitude ranges
        lat_range = (45, 75)
        lon_range = (-175, -130)
        
        # Apply range filter
        outside_range = ~df['Latitude'].between(*lat_range) | ~df['Longitude'].between(*lon_range)

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
        p = cs.CSprojection((np.rad2deg(lo[lo.size//2]), np.rad2deg(la[lo.size//2])), orientation = v_enu[:2])
        grid = cs.CSgrid(p, 2000.e3, 1000.e3, 40.e3, 50.e3, R = (6371.2 + 110) * 1e3)
        
        model = lompe.Emodel(grid, (lambda lon, lat: conductance(lon, lat, 'h'), lambda lon, lat: conductance(lon, lat, 'p')))

        vlos = ["VsatC", "VsatE", "VsatN"][t0]

        dB = np.vstack((df.Be.values, df.Bn.values, df.Bu.values))
        coords = np.vstack((df.Longitude.values, df.Latitude.values, (6371.2 + height) * 1e3))
        swarm_mag_c_data = lompe.Data(values = dB * 1e-9, coordinates = coords, datatype = 'space_mag_full', iweight=0.3)
        
        #savefile = savepath + str(t0).replace(' ','_').replace(':','')
        #lompe.lompeplot(model, include_data = True, time = t0, apex = a, savekw = {'fname': savefile, 'dpi' : 200})
        
        current_time += dt.timedelta(minutes=1)
    
    
    return swarm_mag_c_data



# These files contain entire AMISR experiment. Function to select from a smaller time interval is needed:
def prepare_data(ke, kn, kz, Vlos, glat, glon, galt, Midtime, t0, t1):
    """ get data from correct time period """

    Tidx1 = np.argmin(np.abs(Midtime[:] - t0)) # will need Tidx1 AND Tidx2
    Tidx2 = np.argmin(np.abs(Midtime[:] - t1)) # number of beams x number of bins - 

    print('Vlos', Vlos[Tidx1:Tidx2, :, :].shape) 
    
    glat_new = np.tile(glat, (Tidx2 - Tidx1, 1, 1)) # expanded, to flatten later
    glon_new = np.tile(glon, (Tidx2 - Tidx1, 1, 1)) # expanded, to flatten later
    
    print("glat shape: ", glat.shape)
    print("glat (tile'd') shape:" , glat_new.shape)
    print("glon shape: ", glon.shape)
    print("glon (tile'd') shape:" , glon_new.shape)
    coords = np.array([glon_new.flatten(), glat_new.flatten()])
    print("coords shape: ", coords.shape)
    
    
    vlos_input = Vlos[Tidx1:Tidx2, :, :] # no beams x no records x no bins - will need to flatten beams&time
    print("vlos input shape: ",vlos_input.shape)
    # estimate parallel velocity here instead of finding theta - FAV=0, no LOS diff
    cos_theta_input = (np.sqrt(ke**2+kn**2)/(np.sqrt(ke**2+kn**2+kz**2)))
    print('cos theta shape: ',cos_theta_input.shape)
    vlos=(vlos_input/cos_theta_input).flatten()
    vlos[np.abs(vlos)>5000.] = np.nan #quick fix for vertical, FA beams
    # beam filtering - scaling vertical components - uncertainties
    print("vlos shape: ",vlos.shape)
    # print("vlos used for calculations: ", vlos)
    
    ke_norm = ke/np.sqrt(ke**2+kn**2)
    kn_norm = kn/np.sqrt(ke**2+kn**2)
    ke_norm_new = np.tile(ke_norm, (Tidx2 - Tidx1, 1, 1)) # expand out to later flatten
    kn_norm_new = np.tile(kn_norm, (Tidx2 - Tidx1, 1, 1)) # expand out to later flatten
    
    print("ke_norm shape: ",ke_norm.shape)
    print("kn_norm shape: ",kn_norm.shape)
    print("ke_norm shape: ",ke_norm_new.shape)
    print("kn_norm shape: ",kn_norm_new.shape)
    
    los = np.array([ke_norm_new.flatten(), kn_norm_new.flatten()])
    print("los shape: ",los.shape)
    
    pfisr_data = lompe.Data(vlos, coordinates = coords, LOS = los, datatype = 'convection', scale = None) # vlos - no time records x no beams  no range gates 
    # duplicate for coords and los - use np.tile() to do this - flatten to keep shape
    #print("prepared vlos: ", vlos)
    #print("prepared los: ", los)
    
    return pfisr_data



def conductance(lon, lat, type):
    sza = lompe.conductance.sunlight.sza(lat, lon, t0, degrees=True)

    return(lompe.conductance.EUV_conductance(sza, hallOrPed= type))

