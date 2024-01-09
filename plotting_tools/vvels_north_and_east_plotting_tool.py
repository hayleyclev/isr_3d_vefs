#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 29 00:46:54 2023

@author: clevenger
"""

#matplotlib inline
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
#import re
import h5py
import numpy as np
# import io_utils #custom wrapper for pytables

# Download the vector velocity data file that we need to run these examples
import os
vfilepath='/Users/clevenger/Projects/lompe_pfisr/test_datasets/20170616.001_lp_1min-fitcal-vvelsLat-60sec.h5'
if not os.path.exists(vfilepath):
    import urllib.request
    url='https://data.amisr.com/database/dbase_site_media/PFISR/Experiments/20170616.001/DataFiles/20170616.001_lp_1min-fitcal-vvelsLat-60sec.h5'

    print('Downloading data file...')
    urllib.request.urlretrieve(url,vfilepath)

    print('...Done!')
    
with h5py.File(vfilepath, 'r') as v:
    times=[datetime.datetime(1970,1,1)+datetime.timedelta(seconds=int(t)) for t in v['/Time']['UnixTime'][:,0]]
    #print('times: ',times.shape)
    cgm_lat=0.5*(v['/VectorVels']['MagneticLatitude'][:,0]+v['/VectorVels']['MagneticLatitude'][:,1]) #average bin edges to get centers
    #The Vest array is Nrecords x Nlatitudes x 3 (perp-North, perp-East, parallel)
    vipn=v['/VectorVels']['Vest'][:,:,0]
    #print('vipn: ',vipn.shape)
    dvipn=v['/VectorVels']['errVest'][:,:,0]
    #print('dvipn: ',dvipn.shape)
    vipe=v['/VectorVels']['Vest'][:,:,1]
    #print('vipe: ',vipe.shape)
    dvipe=v['/VectorVels']['errVest'][:,:,1]
    #print('dvipe',dvipe.shape)
    
plt.rcParams['figure.figsize']=10,10
plt.rcParams['font.size']=18
fig,axarr=plt.subplots(2,2,sharex=True,sharey=True)

vclrs=axarr[0,0].pcolormesh(mdates.date2num(times),cgm_lat,vipn.T,vmin=-1000,vmax=1000,cmap='RdBu_r',shading='nearest')
errclrs=axarr[1,0].pcolormesh(mdates.date2num(times),cgm_lat,dvipn.T,vmin=0,vmax=300,cmap='viridis',shading='nearest')

vclrs=axarr[0,1].pcolormesh(mdates.date2num(times),cgm_lat,vipe.T,vmin=-1000,vmax=1000,cmap='RdBu_r',shading='nearest')
errclrs=axarr[1,1].pcolormesh(mdates.date2num(times),cgm_lat,dvipe.T,vmin=0,vmax=300,cmap='viridis',shading='nearest')

start_time = datetime.datetime(2017, 6, 16, 14, 0, 0)
end_time = datetime.datetime(2017, 6, 16, 15, 0, 0)
#minute_interval=datetime.timedelta(minutes=1)

x_bar_start_time=datetime.datetime(2017,6,16,14,1,0)
x_bar_end_time=datetime.datetime(2017,6,16,14,59,0)

#fig, xarr=plt.subplots(2,2,sharex=True, sharey=True)

axarr[-1, 0].set_xlim([mdates.date2num(start_time), mdates.date2num(end_time)])
axarr[-1, 1].set_xlim([mdates.date2num(start_time), mdates.date2num(end_time)])

hour_interval = 1  # Set the interval for ticks (1 hour in this case)
axarr[-1, 0].set_xticks(np.arange(mdates.date2num(start_time), mdates.date2num(end_time), hour_interval / 24.0))
axarr[-1, 1].set_xticks(np.arange(mdates.date2num(start_time), mdates.date2num(end_time), hour_interval / 24.0))

#axarr[-1,0].set_xlim([mdates.date2num(datetime.datetime(2017,1,1,4,0,0)),mdates.date2num(datetime.datetime(2017,1,1,16,0,0))])
#axarr[-1,0].set_xticks(np.arange(mdates.date2num(datetime.datetime(2019,1,1,4,0,0)),mdates.date2num(datetime.datetime(2019,1,1,16,0,0)),2.0/24.0))
#axarr[-1,1].set_xlim([mdates.date2num(datetime.datetime(2017,1,1,4,0,0)),mdates.date2num(datetime.datetime(2017,1,1,16,0,0))])
#axarr[-1,1].set_xticks(np.arange(mdates.date2num(datetime.datetime(2017,1,1,4,0,0)),mdates.date2num(datetime.datetime(2017,1,1,16,0,0)),2.0/24.0))

axarr[-1,0].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
axarr[-1,0].set_xlabel('UT')
axarr[-1,1].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
axarr[-1,1].set_xlabel('UT')
    
#vertical_line_time = datetime.datetime(2017,6,16,14,1,0)
#axarr[0, 0].axvline(x=vertical_line_time, color='magenta', linestyle='-')
#axarr[0, 1].axvline(x=vertical_line_time, color='turquoise', linestyle='-')
#axarr[1, 0].axvline(x=vertical_line_time, color='magenta', linestyle='-')
#axarr[1, 1].axvline(x=vertical_line_time, color='magenta', linestyle='-')

axarr[0,0].set_ylabel('CGM Latitude')
axarr[1,0].set_ylabel('CGM Latitude')

axarr[0,0].set_title('Vector Velocity North')
axarr[0,1].set_title('Vector Velocity East')

axarr[1,0].set_title('Velocity North Error')
axarr[1,1].set_title('Velocity East Error')

fig.suptitle('Vector Velocities from Long Pulses on 2017-06-16')

box=axarr[0,1].get_position()
vcbarax=fig.add_axes([box.x0+box.width+0.01, box.y0, 0.025, box.height])
vcb=plt.colorbar(vclrs,cax=vcbarax)
vcb.set_label('Velocity (m/s)')

box=axarr[1,1].get_position()
errcbarax=fig.add_axes([box.x0+box.width+0.01, box.y0, 0.025, box.height])
errcb=plt.colorbar(errclrs,cax=errcbarax)
errcb.set_label('Error (m/s)')
    
#minute_str=start_time.strftime('%M')
#figure_filename='/Users/clevenger/Projects/lompe_pfisr/test_datasets/figure_{minute_str}.png'
#plt.savefig(figure_filename,dpi=300)
#plt.close()



