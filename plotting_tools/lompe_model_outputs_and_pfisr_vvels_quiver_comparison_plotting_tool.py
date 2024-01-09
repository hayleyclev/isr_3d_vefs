#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 10:08:34 2023

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

vvels_fn = '/Users/clevenger/Projects/vvels/outputs/20170616.001_lp_1min-fitcal-vvels_lat.h5'

with h5py.File(vvels_fn,"r") as h5:
    alt=h5["VvelsGeoCoords/Altitude"][:,0]
    print(alt)
    alt_ind = np.argmin(np.abs(alt-300))
    print(alt_ind)
    lat=h5["VvelsGeoCoords/Latitude"][:,alt_ind]
    lon=h5["VvelsGeoCoords/Longitude"][:,alt_ind]
    vel=h5["VvelsGeoCoords/Velocity"][50,:,alt_ind,:-1] # 50 is made up, change as needed
    #utime = h5['Time/UnixTime'][:] 
    
#print(utime.shape)
print(lat.shape)
print(lon.shape)
print("vel shape: ", vel.shape)

# nc_fn = '/Users/clevenger/Projects/lompe_pfisr/lompe_output_xarray_2017-06-16_140100.nc'
# ds = xr.open_dataset(nc_fn)

# ve = [-68.78677844, -114.34123498, -126.14397326,  -79.88758934,   21.06542361,
#       175.86382754,  324.27985754,  234.69834643, -385.04044252,  -76.65650558,
#       -157.95803706, -198.67251404, -155.2267829,    49.78067124,  209.658857,
#       328.53178719,  180.80940107, -337.38386279,  -55.35682649, -188.69098236,
#       -273.76939386, -265.93079138,  133.81609265,  234.41344131,  370.87857144,
#       384.2609289,   -21.52290896,   15.20170127, -164.78023521, -340.47221123,
#       -506.70740762,  175.17431601,  136.85734273,  194.68396026,  229.28109513,
#       120.76774493,  133.21130249,  -45.51647904, -272.25804366, -618.49925003,
#       -18.98120975,  362.90490311,  258.49842091,   44.59157384,  327.22040272,
#       254.97232012,   88.48908119, -219.97021414, -646.23478314, -362.64827618,
#       389.14613204,  482.34456454,    4.94045191,  -84.99025496,  332.20144901,
#       217.72714482,  -15.17906524, -597.02664268, -559.20472797,  610.27762983,
#       771.1358565,   470.61099694,  166.66867616,  310.84591876,  199.03582013,
#       4.85053712, -468.93490898, -621.02326518,  473.61656851,  786.56242427,
#       534.39887884,  375.9541638,   210.72473914,   51.63681762, -230.95430965,
#       -638.62335743, -547.45299988,   90.94499701,  456.82583809,  423.08470843,
#       339.13367751]

# vn = [169.70269394,   145.82156068,   108.09534239,    84.5851118,
#       110.42917358,   230.47864242,   455.45930674,   447.23976387,
#       146.09057162,   234.07413177,   216.07506377,   176.17688832,
#       116.53842303,  230.32321784,   464.46354616,   534.28653125,
#       420.11021292,   286.05624255,   295.61829974,   282.29366801,
#       231.73481004,   139.07606444,   300.18036767,   266.65733012,
#       101.98538328,   -14.21571626,  -235.92593316,   330.27344992,
#       360.66839394,   369.05336183,   129.1642849,    208.21415123,
#       149.03362339,   104.63076656,  -186.53612523,  -413.96034039,
#       279.70330957,   274.87604519,   152.5248586,    -68.94556722,
#       -138.97583425,  -258.20646501,  -304.71220026,  -646.27253552,
#       -702.65876657,   137.99909803,    91.85135497,    -4.5461629,
#       -306.41288215,  -554.93013718,  -581.97371607,  -517.23364324,
#       -272.4448629,    -69.1761475,    -76.04773289,  -223.46319956,
#       -438.54504232,  -876.40735155, -1338.22149292,  -883.99095152,
#       -420.95773403,  -388.73868206,  -347.37591975,  -278.15577558,
#       -526.12256104,  -921.11714157, -1418.98230778, -1191.83423553,
#       -281.03910742,  -202.06583868,  -317.3825921,   -278.5596242,
#       -365.0214375,   -568.13229256,  -770.76579348,  -770.35900035,
#       -302.13599413,   139.88651925,   108.49844938,   -39.97390049,
#       -99.45413309]


# #alt=h5["VvelsGeoCoords/Altitude"][:,0]
# #print(alt)
# #alt_ind = np.argmin(np.abs(alt-300))
# #print(alt_ind)
# lat=ds['lat'].values
# lon=ds['lon'].values
# #vel=ds["VvelsGeoCoords/Velocity"][:,:,alt_ind,:]
# #utime = h5['Time/UnixTime'][:] 
# #efield_e = ds['efield_E'].values
# #efield_n = ds['efield_N'].values

#ve = np.array(ve).reshape(lat.shape)
#vn = np.array(vn).reshape(lat.shape)
    
#print(utime.shape)
#print(lat.shape)
#print(lon.shape)
#print("vel shape: ", vel.shape)

# query
# error filtering
# check against summary plots
# any time errVelocity >500m/s NaN
# diff - point by point comparison
# diff - show as quiver plot

# use load_model here
# load in model object
# use model.v() - use vvels as input to this function
# cut out 3rd dim for vu - nans or cut off

# create vel attribute

save_fn = '/Users/clevenger/Projects/lompe_pfisr/lompe_output_xarray_2017-06-16_140400.nc'
model = load_model(save_fn)
lompe_ve, lompe_vn = model.v(lat, lon) 
print("lompe_ve shape: ", lompe_ve.shape)
print("lompe_vn shape: ", lompe_vn.shape)


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

s = 150

#ax_map.plot(lon, lat, linewidth=3, color='red', label='High Flier', transform=ccrs.Geodetic())
u, v = scale_uv(lon, lat, vel[:,0], vel[:,1])
Q = ax_map.quiver(lon, lat, u, v, zorder=5, scale=10, color='green', transform=ccrs.PlateCarree())

u, v = scale_uv(lon, lat, lompe_ve, lompe_vn)
Q = ax_map.quiver(lon, lat, u, v, zorder=5, scale=10, color='red', transform=ccrs.PlateCarree())


# ax_map.plot(LF_data['glon'][::s], LF_data['glat'][::s], linewidth=3, color='blue', label='Low Flier', transform=ccrs.Geodetic())
# u, v = scale_uv(LF_data['glon'][::s], LF_data['glat'][::s], LF_data['EE'][::s], LF_data['EN'][::s])
# Q = ax_map.quiver(LF_data['glon'][::s], LF_data['glat'][::s], u, v, zorder=5, scale=1, linewidth=2, color='green', headlength=0, headwidth=0, headaxislength=0, transform=ccrs.PlateCarree())

ax_map.quiverkey(Q, 0.4, 0.2, 0.1, 'E=100mV/m', labelpos='E', transform=ax_map.transAxes)
ax_map.legend()

plt.savefig('dce_map.png')
plt.show()

# error - diffs, plots
np.set_printoptions(threshold=np.inf)
print(vel)


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





