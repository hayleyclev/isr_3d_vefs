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
savepath = '../temp_outputs'
apex = apexpy.Apex(int(event[0:4]), refh = 110)

# supermagfn = '/Users/hayleyclev/Desktop/lompe/demo/data_sets/20120405_supermag.h5'
# superdarnfn = '/Users/hayleyclev/Desktop/lompe/demo/data_sets/20120405_superdarn_grdmap.h5'
# iridiumfn = '/Users/hayleyclev/Desktop/lompe/demo/data_sets/20120405_iridium.h5'
pfisrfn = '/Users/e30737/Desktop/Data/AMISR/PFISR/2017/20170616.001_lp_1min-fitcal.h5'

# set up grid
position = (-147, 65) # lon, lat
orientation = (0, 1) # east, north
L, W, Lres, Wres = 500e3, 500e3, 10.e3, 10.e3 # dimensions and resolution of grid
grid = lompe.cs.CSgrid(lompe.cs.CSprojection(position, orientation), L, W, Lres, Wres, R = 6481.2e3)

# load ampere, supermag, and superdarn data from 2012-05-05
# ampere    = pd.read_hdf(iridiumfn)
# supermag  = pd.read_hdf(supermagfn)
# superdarn = pd.read_hdf(superdarnfn)
# pfisr_read = pd.read_hdf(pfisrfn)
# print(pfisr_read)

with h5py.File(pfisrfn,"r") as h5:
    Vlos = h5['FittedParams/Fits'][:,:,:,-1,3]
    print(Vlos.shape)
    glat = h5['Geomag/Latitude'][:]
    glon = h5['Geomag/Longitude'][:]
    galt = h5['Geomag/Altitude'][:]
    utime = h5['Time/UnixTime'][:]
    print(utime.shape)
    ke = h5['Geomag/ke'][:]
    kn = h5['Geomag/kn'][:]
    kz = h5['Geomag/kz'][:]


print(glat.shape, glon.shape, galt.shape)
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
    print(t0.timestamp())
    print(t1.timestamp())
    Tidx1 = np.argmin(np.abs(utime[:,0]- t0.timestamp()))
    #Tidx2 = np.argmin(np.abs(utime[:,0]- t1.timestamp()))
    Tidx2 = Tidx1 + 1
    print(Tidx1)
    print(Tidx2)
    # np.reshape // np.tile // np.repeat
    # vlos = Vlos[Tidx1:Tidx2,:,:]
    coords = np.array([glon.flatten(), glat.flatten()])
    #coords = np.repeat(coords_input, 1)
    cos_theta = (np.sqrt(ke**2+kn**2)/(np.sqrt(ke**2+kn**2+kz**2)))
    ke_norm = ke/np.sqrt(ke**2+kn**2)
    kn_norm = kn/np.sqrt(ke**2+kn**2)
    vlos_input = np.squeeze(Vlos[Tidx1:Tidx2,:,:])
    vlos = (vlos_input/cos_theta).flatten()
    #vlos = np.reshape(vlos_input,(1,1))
    los = np.array([ke_norm.flatten(), kn_norm.flatten()])
    #los = np.reshape(los_input,(1,1))
    print(vlos.shape, coords.shape, los.shape)
    pfisr_data = lompe.Data(vlos, coordinates = coords, LOS = los, datatype = 'convection')
    
    return pfisr_data

# get figures from entire day and save somewhere

# times during entire day
times = pd.date_range('2017-06-16 14:00', '2017-06-16 15:00', freq = '1Min')
DT = timedelta(seconds = 30) # will select data from +- DT


Kp = 1 # for Hardy conductance model
SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, 5, times[0], 'hall'    )
SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, 5, times[0], 'pedersen')
model = lompe.Emodel(grid, Hall_Pedersen_conductance = (SH, SP))


    
# loop through times and save
for t in times[1:]:
    print(t)
    
    SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, 5, t, 'hall'    )
    SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, 5, t, 'pedersen')

    model.clear_model(Hall_Pedersen_conductance = (SH, SP)) # reset
    
    pfisr_data = prepare_data(t - DT, t + DT)
    
    model.add_data(pfisr_data)

    gtg, ltl = model.run_inversion(l1 = 2, l2 = 0)
    
    savefile = savepath + str(t).replace(' ','_').replace(':','')
    lompe.lompeplot(model, include_data = True, time = t, apex = apex, savekw = {'fname': savefile, 'dpi' : 200})


