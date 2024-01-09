#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 05:18:07 2023

@author: clevenger
"""

import numpy as np
import h5py
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
#import cartopy.crs as ccrs
import datetime

filename_lp = '/Users/clevenger/Projects/lompe_pfisr/test_datasets/20170616.001_lp_1min-fitcal.h5'
#filename_ac = 'data/20200207.001_ac_5min-fitcal.h5'

alt_min = 150e3
alt_max = 400e3

start_time = np.datetime64('2017-06-16T14:00:00')
end_time = np.datetime64('2017-06-16T15:05:00')

with h5py.File(filename_lp, 'r') as h5:
    beamcodes = h5['BeamCodes'][:]
    bidx = np.argmax(beamcodes[:,2])
    alt_lp = h5['FittedParams/Altitude'][bidx,:]
    ne_lp = h5['FittedParams/Ne'][:,bidx,:]
    ti_lp = h5['FittedParams/Fits'][:,bidx,:,0,1]
    te_lp = h5['FittedParams/Fits'][:,bidx,:,-1,1]
    vlos_lp = h5['FittedParams/Fits'][:,bidx,:,0,3]
    utime_lp = h5['Time/UnixTime'][:,0]

time_lp = utime_lp.astype('datetime64[s]')
ne_lp = ne_lp[:,np.isfinite(alt_lp)]
ti_lp = ti_lp[:,np.isfinite(alt_lp)]
te_lp = te_lp[:,np.isfinite(alt_lp)]
vlos_lp = vlos_lp[:,np.isfinite(alt_lp)]
alt_lp = alt_lp[np.isfinite(alt_lp)]

#with h5py.File(filename_ac, 'r') as h5:
#    beamcodes = h5['BeamCodes'][:]
#    bidx = np.argmax(beamcodes[:,2])
#    alt_ac = h5['FittedParams/Altitude'][bidx,:]
#    ne_ac = h5['FittedParams/Ne'][:,bidx,:]
#    ti_ac = h5['FittedParams/Fits'][:,bidx,:,0,1]
#    te_ac = h5['FittedParams/Fits'][:,bidx,:,-1,1]
#    vlos_ac = h5['FittedParams/Fits'][:,bidx,:,-1,3]
#    utime_ac = h5['Time/UnixTime'][:,0]

#time_ac = utime_ac.astype('datetime64[s]')
#ne_ac = ne_ac[:,np.isfinite(alt_ac)]
#ti_ac = ti_ac[:,np.isfinite(alt_ac)]
#te_ac = te_ac[:,np.isfinite(alt_ac)]
#vlos_ac = vlos_ac[:,np.isfinite(alt_ac)]
#alt_ac = alt_ac[np.isfinite(alt_ac)]

alt_ind = (alt_lp >= alt_min) & (alt_lp <= alt_max)
time_ind = (time_lp >= start_time) & (time_lp <= end_time)

ne_lp = ne_lp[time_ind][:, alt_ind]
ti_lp = ti_lp[time_ind][:, alt_ind]
te_lp = te_lp[time_ind][:, alt_ind]
vlos_lp = vlos_lp[time_ind][:, alt_ind]
alt_lp = alt_lp[alt_ind]
time_lp = time_lp[time_ind] 

cutoff_alt = 150.*1000.
#aidx_ac = np.argmin(np.abs(alt_ac-cutoff_alt))
aidx_lp = np.argmin(np.abs(alt_lp-cutoff_alt))


fig = plt.figure(figsize=(20,15))
gs = gridspec.GridSpec(4,1)

for hour in range(14, 15):  # You can adjust the start and end hours as needed
    for minute in range(0, 60):
        vertical_line_time = datetime.datetime(2017, 6, 16, hour, minute, 0)

        # Plot Electron Density
        ax0 = fig.add_subplot(gs[0])
        #c = ax.pcolormesh(time_ac, alt_ac[:aidx_ac], ne_ac[:,:aidx_ac].T, vmin=0., vmax=4.e11, cmap='viridis')
        c = ax0.pcolormesh(time_lp, alt_lp[aidx_lp:], ne_lp[:,aidx_lp:].T, vmin=0., vmax=4.e11, cmap='viridis')
        #ax.axvline(x=vertical_line_time, color='magenta', linestyle='-', lw=4)
        # ax.set_xlabel('Universal Time')
        ax0.set_ylabel('Altitude (m)')
        fig.colorbar(c, label=r'Electron Density (m$^{-3}$)')

        # Plot Ion Temperature
        ax1 = fig.add_subplot(gs[1])
        #c = ax.pcolormesh(time_ac, alt_ac[:aidx_ac], ti_ac[:,:aidx_ac].T, vmin=0., vmax=3.e3, cmap='magma')
        c = ax1.pcolormesh(time_lp, alt_lp[aidx_lp:], ti_lp[:,aidx_lp:].T, vmin=0., vmax=3.e3, cmap='magma')
        #ax.axvline(x=vertical_line_time, color='cyan', linestyle='-', lw=4)
        # ax.set_xlabel('Universal Time')
        ax1.set_ylabel('Altitude (m)')
        fig.colorbar(c, label=r'Ion Temperature (K)')
        
        # Plot Electron Temperature
        ax2 = fig.add_subplot(gs[2])
        #c = ax.pcolormesh(time_ac, alt_ac[:aidx_ac], te_ac[:,:aidx_ac].T, vmin=0., vmax=5.e3, cmap='inferno')
        c = ax2.pcolormesh(time_lp, alt_lp[aidx_lp:], te_lp[:,aidx_lp:].T, vmin=0., vmax=5.e3, cmap='inferno')
        #ax.axvline(x=vertical_line_time, color='cyan', linestyle='-', lw=4)
        # ax.set_xlabel('Universal Time')
        ax2.set_ylabel('Altitude (m)')
        fig.colorbar(c, label=r'Electron Temperature (K)')

        # Plot Line-of-Site Velocity
        ax3 = fig.add_subplot(gs[3])
        #c = ax.pcolormesh(time_ac, alt_ac[:aidx_ac], vlos_ac[:,:aidx_ac].T, vmin=-500., vmax=500., cmap='bwr')
        c = ax3.pcolormesh(time_lp, alt_lp[aidx_lp:], vlos_lp[:,aidx_lp:].T, vmin=-500., vmax=500., cmap='bwr')
        #ax.axvline(x=vertical_line_time, color='yellow', linestyle='-', lw=4)
        ax3.set_xlabel('Universal Time')
        ax3.set_ylabel('Altitude (m)')
        fig.colorbar(c, label=r'Line-of-Site Velocity (m/s)')
        
        ax0.axvline(x=vertical_line_time, color='magenta', linestyle='-', lw=4)
        ax1.axvline(x=vertical_line_time, color='cyan', linestyle='-', lw=4)
        ax2.axvline(x=vertical_line_time, color='cyan', linestyle='-', lw=4)
        ax3.axvline(x=vertical_line_time, color='yellow', linestyle='-', lw=4)
        
    plt.show()






