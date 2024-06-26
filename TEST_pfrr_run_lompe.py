#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 00:02:17 2024

@author: clevenger
"""

# pfrr_run_lompe.py

import numpy as np
import apexpy
import lompe
from lompe.utils.conductance import hardy_EUV
from lompe.utils.save_load_utils import save_model
#import h5py
import os
import pfisr_datahandler as pfisr
import mag_datahandler as mag
#import TEST_swarm_mag_a_datahandler as amag
#import TEST_swarm_mag_b_datahandler as bmag
#import TEST_swarm_mag_c_datahandler as cmag
#import swarm_a_flow_datahandler as aflow
#import swarm_b_flow_datahandler as bflow
#import swarm_c_flow_datahandler as cflow

#def run_lompe_pfisr(start_time, end_time, time_step, Kp, x_resolution, y_resolution,
 #                   plot_save_outdir=None, nc_save_outdir=None, pfisrfn=None, pokermagfn=None, include_swarm_mag_a=False, 
  #                  include_swarm_mag_b=False, include_swarm_mag_c=False):
    
def run_lompe_pfisr(start_time, end_time, time_step, Kp, x_resolution, y_resolution,
                    plot_save_outdir=None, nc_save_outdir=None, pfisrfn=None, pokermagfn=None):

    time0 = [start_time+time_step*i for i in range(int((end_time-start_time)/time_step))]
    time1 = [t0+time_step for t0 in time0]
    time_intervals = np.array([time0, time1]).T
    #print(time_intervals)

    ## times during entire day
    #starttime = pd.date_range(start_time, end_time, freq=freq) # no data in some minutes - figure that out
    ## DT currently doesn't matter - only selecting 1 timestamp based on t0
    #DT = timedelta(seconds = time_step) # will select data from +- DT
    #endtime = starttime + DT
    #time_intervals = pd.DataFrame(data={'starttime':starttime, 'endtime':endtime})
    #print(time_intervals)

    apex = apexpy.Apex(start_time, refh = 110)

    # set up grid
    position = (-147, 65) # lon, lat
    orientation = (-1, 2) # east, north
    L, W, Lres, Wres = 1000e3, 1000e3, x_resolution, y_resolution # dimensions and resolution of grid
    grid = lompe.cs.CSgrid(lompe.cs.CSprojection(position, orientation), L, W, Lres, Wres, R = 6481.2e3)

    # set up conductances and model
    SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, time_intervals[0], 'hall'    )
    SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, time_intervals[0], 'pedersen')
    model = lompe.Emodel(grid, Hall_Pedersen_conductance = (SH, SP))

    # Collect datasets here
    if pfisrfn:
        pfisr_data = pfisr.collect_data(pfisrfn, time_intervals)
    if pokermagfn:
        mag_data = mag.collect_data(pokermagfn, time_intervals)
        
    #swarm_a_mag_data = amag.collect_data(start_time, end_time)
    #swarm_b_mag_data = bmag.collect_data(start_time, end_time)
    #swarm_c_mag_data = cmag.collect_data(start_time, end_time)
    
    #swarm_a_flow_data = aflow.collect_data(start_time, end_time)
    #swarm_b_flow_data = bflow.collect_data(start_time, end_time)
    #swarm_c_flow_data = cflow.collect_data(start_time, end_time)
    

    # loop through times and save
    #for i, row in time_intervals.iterrows():
    for i, (stime, etime) in enumerate(time_intervals):
        t = stime
        print("t: ",t)
    
        SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, t, 'hall'    )
        SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, t, 'pedersen')

        model.clear_model(Hall_Pedersen_conductance = (SH, SP)) # reset
    
        # add datasets for this time
        if pfisrfn:
            model.add_data(pfisr_data[i])
        if pokermagfn:
            model.add_data(mag_data[i])
            
        #swarm_a_mag_data = amag.collect_data(start_time, end_time)
        #model.add_data(swarm_a_mag_data)
        
        #swarm_b_mag_data = bmag.collect_data(start_time, end_time)
        #model.add_data(swarm_b_mag_data)
        
        #swarm_c_mag_data = cmag.collect_data(start_time, end_time)
        #model.add_data(swarm_c_mag_data)
        
        #swarm_a_flow_data = aflow.collect_data(start_time, end_time)
        #model.add_data(swarm_a_flow_data)
            
        #swarm_b_flow_data = bflow.collect_data(start_time, end_time)
        #model.add_data(swarm_b_flow_data)
        
        #swarm_c_flow_data = cflow.collect_data(start_time, end_time)
        #model.add_data(swarm_c_flow_data)
        
        #if include_swarm_mag_a:
         #   swarm_a_mag_data = amag.collect_data(start_time, end_time)
          #  model.add_data(swarm_a_mag_data)
            
        #if include_swarm_mag_b:
         #   swarm_b_mag_data = bmag.collect_data(start_time, end_time)
          #  model.add_data(swarm_b_mag_data)
            
        #if include_swarm_mag_c:
         #   swarm_c_mag_data = cmag.collect_data(start_time, end_time)
          #  model.add_data(swarm_c_mag_data)

        #SD_data = fitacf_get_lompe(fn, starttime, endtime)
        #model.add_data(SD_data)

        # run model
        gtg, ltl = model.run_inversion(l1 = 2, l2 = 0.1)
    

        # USE FOR SAVING MODEL PLOTS
        savefile = os.path.join(plot_save_outdir,str(t).replace(' ','_').replace(':',''))
        print(savefile)
        lompe.lompeplot(model, include_data = True, time = t, apex = apex, savekw = {'fname': savefile, 'dpi' : 200})

        # USE FOR SAVING MODEL NCs
        savefile = os.path.join(nc_save_outdir,str(t).replace(' ','_').replace(':','')+'.nc') # create directory to save output as nc to read in
        save_model(model, file_name=savefile) # one file per time stamp
        
        # pathlib; os.path for filenames/outdirs