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

event = '2017-06-16'
savepath = 'C:/Users/hzibi/Projects/lompe_demo/AMISR/PFISR_demofigs/'
apex = apexpy.Apex(int(event[0:4]), refh = 110)

# supermagfn = '/Users/hayleyclev/Desktop/lompe/demo/data_sets/20120405_supermag.h5'
# superdarnfn = '/Users/hayleyclev/Desktop/lompe/demo/data_sets/20120405_superdarn_grdmap.h5'
# iridiumfn = '/Users/hayleyclev/Desktop/lompe/demo/data_sets/20120405_iridium.h5'
pfisrfn = 'C:/Users/hzibi/Projects/lompe_demo/AMISR/06162017/20170616.001_lp_1min-fitcal.h5'

# set up grid
position = (-147, 65) # lon, lat
orientation = (-1, 2) # east, north
L, W, Lres, Wres = 500e3, 500e3, 50.e3, 50.e3 # dimensions and resolution of grid
grid = lompe.cs.CSgrid(lompe.cs.CSprojection(position, orientation), L, W, Lres, Wres, R = 6481.2e3)

# load ampere, supermag, and superdarn data from 2012-05-05
# ampere    = pd.read_hdf(iridiumfn)
# supermag  = pd.read_hdf(supermagfn)
# superdarn = pd.read_hdf(superdarnfn)
# pfisr_read = pd.read_hdf(pfisrfn)
# print(pfisr_read)

with h5py.File(pfisrfn,"r") as h5:
    Vlos = h5['FittedParams/Fits'][:,:,:,-1,3]
    #print("Vlos shape: ",Vlos_input.shape)
    #Vlos=Vlos_input.reshape(Vlos_input.shape[0],-1)
    print("Vlos reshaped: ",Vlos.shape)
    glat = h5['Geomag/Latitude'][:]
    glon = h5['Geomag/Longitude'][:]
    galt = h5['Geomag/Altitude'][:]
    #glat_reshaped=glat.reshape(-1,glat.shape[-1]*glat.shape[-2])
    #glon_reshaped=glon.reshape(-1,glon.shape[-1]*glon.shape[-2])
    #galt_reshaped=galt.reshape(-1,galt.shape[-1]*galt.shape[-2])
    utime = h5['Time/UnixTime'][:]
    print("utime shape: ",utime.shape)
    
    ke = h5['Geomag/ke'][:]
    kn = h5['Geomag/kn'][:]
    kz = h5['Geomag/kz'][:]
    print("ke shape: ",ke.shape,"kn shape: ",kn.shape,"kz.shape: ",kz.shape)
    #ke_reshaped=ke.reshape(-1,ke.shape[-1]*ke.shape[-2])
    #kn_reshaped=kn.reshape(-1,kn.shape[-1]*kn.shape[-2])
    #kz_reshaped=kz.reshape(-1,kz.shape[-1]*kz.shape[-2])
    #print("ke reshape: ",ke_reshaped.shape,"kn reshape: ",kn_reshaped.shape,"kz.shape: ",kz_reshaped.shape)

print("glat shape: ",glat.shape, "glon shape: ",glon.shape, "galt shape: ",galt.shape)
#print("glat reshape: ",glat_reshaped.shape, "glon reshape: ",glon_reshaped.shape, "galts reshape: ",galt_reshaped.shape)
# these files contain entire day. Function to select from a smaller time interval is needed:
def prepare_data(t0, t1):
    """ get data from correct time period """
    # prepare ampere
    # amp = ampere[(ampere.time >= t0) & (ampere.time <= t1)]
    # B = np.vstack((amp.B_e.values, amp.B_n.values, amp.B_r.values))
    # coords = np.vstack((amp.lon.values, amp.lat.values, amp.r.values))
    # amp_data = lompe.Data(B * 1e-9, coords, datatype = 'space_mag_fac', scale = 200e-9)

    # prepare supermag
    # sm = supermag[t0:t1]
    # B = np.vstack((sm.Be.values, sm.Bn.values, sm.Bu.values))
    # coords = np.vstack((sm.lon.values, sm.lat.values))
    # sm_data = lompe.Data(B * 1e-9, coords, datatype = 'ground_mag', scale = 100e-9)

    # prepare superdarn
    # Tidx1 = np.argmin(np.abs(utime[:,0]-np.datetime64('2017-06-16 14:00').astype(int)))
    # Tidx1 = np.argmin(np.abs(utime[:, 0] - np.datetime64('2017-06-16 14:00').astype('timedelta64[s]')))
    # Tidx2 = np.argmin(np.abs(utime[:,0]-np.datetime64('2017-06-16 15:00').astype(int)))
    # Tidx2 = np.argmin(np.abs(utime[:, 0] - np.datetime64('2017-06-16 15:00').astype('timedelta64[s]')))
    # utime_sec = utime[:, 0] // 1_000_000
    # t0_unix_sec = np.datetime64('2017-06-16 14:00').astype('datetime64[s]').astype(int)
    # t1_unix_sec = np.datetime64('2017-06-16 15:00').astype('datetime64[s]').astype(int)
    # Tidx1 = np.argmin(np.abs(utime[:, 0] // 1_000_000 - t0_unix_sec))
    # Tidx2 = np.argmin(np.abs(utime[:, 0] // 1_000_000 - t1_unix_sec))
    # Tidx1 = np.argmin(np.abs(utime_sec - t0_unix_sec))
    # Tidx2 = np.argmin(np.abs(utime_sec - t1_unix_sec))
    # def get_unixtime(dt64):
        # return dt64.astype('datetime64[s]').astype('int')
    # t0 = np.datetime64('2017-06-16 14:00').astype('datetime64[s]').astype(int)
    # t1 = np.datetime64('2017-06-16 15:00').astype('datetime64[s]').astype(int)
    # df = pd.DataFrame({'time': [pd.to_datetime('2019-01-15 13:25:43')]})
    # df_unix_sec = pd.to_datetime(df['time'], unit='ms', origin='unix')
    print("t0 timestamp: ",t0.timestamp())
    print("t1 timestamp: ",t1.timestamp())
    
    Tidx1 = np.argmin(np.abs(utime[:,0]- t0.timestamp()))
    #Tidx2 = np.argmin(np.abs(utime[:,0]- t1.timestamp()))
    Tidx2=Tidx1+1
    print("Tidx1: ",Tidx1)
    print("Tidx2: ",Tidx2)
    
    # np.reshape // np.tile // np.repeat
    # vlos = Vlos[Tidx1:Tidx2,:,:]
    #flatted glat and glon and put next to each other
    print("glat shape:" ,glat.shape)
    print("glon shape:" ,glon.shape)
    #coords_input = np.vstack((glon, glat))
    coords = np.array([glon.flatten(), glat.flatten()])
    #print("coords (input) shape: ",coords_input.shape)
    #get to (2,414)?? tile instead of repeat?
    #coords = np.repeat(coords_input,1)
    print("coords shape: ",coords.shape)
    
    ke_norm = ke/np.sqrt(ke**2+kn**2)
    kn_norm = kn/np.sqrt(ke**2+kn**2)
    #vlos_input = Vlos[Tidx1:Tidx2,:]/cos_theta
    vlos_input=np.squeeze(Vlos[Tidx1:Tidx2,:,:])
    print("vlos input shape: ",vlos_input.shape)
    
    #cos_theta_input = (np.sqrt(ke**2+kn**2)/(np.sqrt(ke**2+kn**2+kz**2)))
    #cos_theta=cos_theta_input[Tidx1:Tidx2].reshape(-1,1)
    cos_theta_input = (np.sqrt(ke**2+kn**2)/(np.sqrt(ke**2+kn**2+kz**2)))
    print('cos theta shape: ',cos_theta_input.shape)

    #vlos = np.reshape(vlos_input,(2,1))
    vlos=(vlos_input/cos_theta_input).flatten()
    #cos_theta=np.tile(cos_theta_input,(1,vlos_input.shape[1]))
    #vlos=np.squeeze(vlos_input/cos_theta)
    print("vlos shape: ",vlos.shape)
    print("cos theta shape: ",cos_theta_input.shape)
    #vlos_reshaped=vlos_input.reshape(-1,vlos_input.shape[2]*vlos_input.shape[-1])
    #num_rows_los_coords=kn.shape[0]*kn.shape[1]
    
    los_input = np.vstack((ke_norm, kn_norm))
    print("los input shape: ",los_input.shape)
    #los = np.reshape(los_input,(1,1))
    #los=los_input.reshape(1,-1,1)
    print("ke_norm shape: ",ke_norm.shape)
    print("kn_norm shape: ",kn_norm.shape)
    los=np.array([ke_norm.flatten(), kn_norm.flatten()])
    print("los shape: ",los.shape)
    #los_reshaped=np.column_stack((ke_reshaped.reshape(-1),kn_reshaped.reshape(-1)))
    #los_reshaped=np.tile(los_reshaped,(vlos_reshaped.shape[0],1))
    #coords_reshaped=np.tile(coords_input.reshape(-1,1),(1,num_rows_los_coords))
    
    pfisr_data = lompe.Data(vlos, coordinates = coords, LOS = los, datatype = 'convection', scale = None)
    
    return pfisr_data

# get figures from entire day and save somewhere

# times during entire day
times = pd.date_range('2017-06-16 14:00', '2017-06-16 15:00', freq = '1Min')
DT = timedelta(seconds = 2 * 60) # will select data from +- DT


Kp = 1 # for Hardy conductance model
SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, 5, times[0], 'hall'    )
SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, 5, times[0], 'pedersen')
model = lompe.Emodel(grid, Hall_Pedersen_conductance = (SH, SP))


    
# loop through times and save
for t in times[1:]:
    print("t: ",t)
    
    SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, 5, t, 'hall'    )
    SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, 5, t, 'pedersen')

    model.clear_model(Hall_Pedersen_conductance = (SH, SP)) # reset
    
    pfisr_data = prepare_data(t - DT, t + DT)
    
    model.add_data(pfisr_data)

    gtg, ltl = model.run_inversion(l1 = 2, l2 = 0)
    
    savefile = savepath + str(t).replace(' ','_').replace(':','')
    lompe.lompeplot(model, include_data = True, time = t, apex = apex, savekw = {'fname': savefile, 'dpi' : 200})

