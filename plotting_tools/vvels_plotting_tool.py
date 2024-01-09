#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 11:12:35 2023

@author: clevenger
"""

import h5py
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

vvels_fn = '/Users/clevenger/Projects/vvels/outputs/20170616.001_lp_1min-fitcal-vvels_lat.h5'

with h5py.File(vvels_fn,"r") as h5:
    alt=h5["VvelsGeoCoords/Altitude"][:,0]
    print(alt)
    alt_ind = np.argmin(np.abs(alt-300))
    print(alt_ind)
    lat=h5["VvelsGeoCoords/Latitude"][:,alt_ind]
    lon=h5["VvelsGeoCoords/Longitude"][:,alt_ind]
    vel=h5["VvelsGeoCoords/Velocity"][:,:,alt_ind,:]
    utime = h5['Time/UnixTime'][:] 
    
print(utime.shape)
print(lat.shape)
print(lon.shape)
print("vel shape: ", vel.shape)

# query
# error filtering
# check against summary plots
# any time errVelocity >500m/s NaN
# diff - point by point comparison
# diff - show as quiver plot

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
#ax_map.set_extent([13,35,72,84], crs=ccrs.PlateCarree())

s = 150

#ax_map.plot(lon, lat, linewidth=3, color='red', label='High Flier', transform=ccrs.Geodetic())
u, v = scale_uv(lon, lat, vel[0,:,0], vel[0,:,1])
Q = ax_map.quiver(lon, lat, u, v, zorder=5, scale=1, linewidth=2, color='green', headlength=0, headwidth=0, headaxislength=0, transform=ccrs.PlateCarree())


# ax_map.plot(LF_data['glon'][::s], LF_data['glat'][::s], linewidth=3, color='blue', label='Low Flier', transform=ccrs.Geodetic())
# u, v = scale_uv(LF_data['glon'][::s], LF_data['glat'][::s], LF_data['EE'][::s], LF_data['EN'][::s])
# Q = ax_map.quiver(LF_data['glon'][::s], LF_data['glat'][::s], u, v, zorder=5, scale=1, linewidth=2, color='green', headlength=0, headwidth=0, headaxislength=0, transform=ccrs.PlateCarree())

ax_map.quiverkey(Q, 0.4, 0.2, 0.1, 'E=100mV/m', labelpos='E', transform=ax_map.transAxes)
ax_map.legend()

plt.savefig('dce_map.png')
plt.show()

# error - diffs, plots
#np.set_printoptions(threshold=np.inf)
#print(vel)
