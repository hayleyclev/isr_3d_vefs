#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 10:15:39 2024

@author: clevenger
"""

import numpy as np
import h5py
import datetime as dt
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr 
from lompe.utils.save_load_utils import load_model


# vvels file and model save location
vvels_fn = '/Users/clevenger/Projects/data_assimilation/march_14/input_data/PFISR/swarmconj/data/vvels/run/20230314.002_lp_1min-fitcal-vvels_lat.h5'
save_fn = '/Users/clevenger/Projects/data_assimilation/march_14/lompe_outputs/509_runs/just_pfisr/pfisr_fov/2023-03-14_065000.nc'
#save_fn = None
save_fn2 = '/Users/clevenger/Projects/data_assimilation/march_14/lompe_outputs/509_runs/just_pfisr_supermag/pfisr_fov/2023-03-14_065000.nc'
#save_fn2 = None

# load lompe model (or multiple if doing many comparisons)
model = load_model(save_fn)
model2 = load_model(save_fn2)

# vvels file stuff - pull velocity info
with h5py.File(vvels_fn, "r") as h5:
    # Find index of closest timestamp in vvels file
    utimes = h5['Time/UnixTime'][:]
    # Extract data based on found index
    alt = h5["VvelsGeoCoords/Altitude"][:, 0]
    alt_ind = np.argmin(np.abs(alt - 300))
    lat = h5["VvelsGeoCoords/Latitude"][alt_ind, :]
    lon = h5["VvelsGeoCoords/Longitude"][alt_ind, :]
    
    vel = h5["VvelsGeoCoords/Velocity"][32, alt_ind, :, :-1]
    utime = utimes[32].astype('datetime64[s]')
    print("utime:", utime)

# lompe file stuff - pull velocity info
lompe_ve, lompe_vn = model.v(lon, lat)
lompe_ve2, lompe_vn2 = model2.v(lon, lat)

#lompe_ve, lompe_vn = model.v(lon, lat) 
print("lompe_ve shape: ", lompe_ve.shape)
print("lompe_vn shape: ", lompe_vn.shape)

print("lompe_ve2 shape: ", lompe_ve2.shape)
print("lompe_vn2 shape: ", lompe_vn2.shape)

def scale_uv(lon, lat, u, v):
    # scaling/rotation of vector to plot in cartopy
    # https://github.com/SciTools/cartopy/issues/1179
    us = u/np.cos(lat*np.pi/180.)
    vs = v
    sf = np.sqrt(u**2+v**2)/np.sqrt(us**2+vs**2)
    return us*sf, vs*sf


plt.rcParams.update({'font.size': 12})
fig = plt.figure()
proj = ccrs.Orthographic(central_longitude=-147.0, central_latitude=65.0) #change lat, lon

ax_map = fig.add_subplot(111, projection=proj)
gl = ax_map.gridlines(color='dimgrey', draw_labels=True)
# gl.top_labels = False
ax_map.coastlines(linewidth=0.5)
ax_map.add_feature(cfeature.LAND, color='whitesmoke')
ax_map.add_feature(cfeature.OCEAN, color='white')
ax_map.set_extent([-150,-140,65,68], crs=ccrs.PlateCarree())

ax_map.set_xlabel('Longitude')
ax_map.set_ylabel('Latitude')


s = 150

#ax_map.plot(lon, lat, linewidth=3, color='red', label='High Flier', transform=ccrs.Geodetic())
u, v = scale_uv(lon, lat, vel[:,0], vel[:,1])
Q = ax_map.quiver(lon, lat, u, v, zorder=5, scale=2000, color='darkorange', transform=ccrs.PlateCarree(), label = 'vvels')

u, v = scale_uv(lon, lat, lompe_ve, lompe_vn)
Q = ax_map.quiver(lon, lat, u, v, zorder=5, scale=2000, color='lime', transform=ccrs.PlateCarree(), label = 'lompe (flows only)')

u, v = scale_uv(lon, lat, lompe_ve2, lompe_vn2)
Q = ax_map.quiver(lon, lat, u, v, zorder=5, scale=2000, color='magenta', transform=ccrs.PlateCarree(), label = 'lompe (flows & mag)')
ax_map.legend(loc='upper left', fontsize='small')


# ax_map.plot(LF_data['glon'][::s], LF_data['glat'][::s], linewidth=3, color='blue', label='Low Flier', transform=ccrs.Geodetic())
# u, v = scale_uv(LF_data['glon'][::s], LF_data['glat'][::s], LF_data['EE'][::s], LF_data['EN'][::s])
# Q = ax_map.quiver(LF_data['glon'][::s], LF_data['glat'][::s], u, v, zorder=5, scale=1, linewidth=2, color='green', headlength=0, headwidth=0, headaxislength=0, transform=ccrs.PlateCarree())

ref_velocity = 1000
#ax_map.quiverkey(Q, 0.4, 0.2, 0.1, ref_velocity, labelpos='E', transform=ax_map.transAxes)
ax_map.legend()
ax_map.legend(loc='lower right', fontsize='small')

plt.savefig('dce_map.png')
plt.show()

# error - diffs, plots
np.set_printoptions(threshold=np.inf)
#print(vel)


#find matching time index for vvels and lompe output
    # run lompe for the entire data set - make it easier for indexing - to keep amount of points same
    # will get 543 .nc's - name as _000, _001, ... _542
    # get rid of 3rd dim velocity (vu) when reading in file

# load model

# select output file based on what time we're looking at - hard code 
# read in vvels file
# load the lompe model using load_model
# use model.v() at vvels lat & lon locations (from vvels input file - see vvels_test to pull)

# time.strftime(‘%Y%m%d_%H%M%S’)

# after working out timing issue
    # set up synthetic data run with vvels plotting
        # original synthetic data vectors, lom