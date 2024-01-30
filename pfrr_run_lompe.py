# pfrr_run_lompe.py

import numpy as np
import pandas as pd
# import datetime
from datetime import timedelta
from lompe.utils.conductance import hardy_EUV
import apexpy
import lompe
import matplotlib.pyplot as plt
import h5py
import os
from lompe.utils.save_load_utils import save_model
plt.ioff()
import pfisr_datahandler as pfisr

def run_lompe_pfisr(start_time, end_time, freq, time_step, Kp, x_resolution, y_resolution, pfisrfn,
                    plot_save_outdir, nc_save_outdir):


    # times during entire day
    starttime = pd.date_range(start_time, end_time, freq=freq) # no data in some minutes - figure that out
    # DT currently doesn't matter - only selecting 1 timestamp based on t0
    DT = timedelta(seconds = time_step) # will select data from +- DT
    endtime = starttime + DT
    time_intervals = pd.DataFrame(data={'starttime':starttime, 'endtime':endtime})
    print(time_intervals)

    apex = apexpy.Apex(starttime[0], refh = 110)

    # set up grid
    position = (-147, 65) # lon, lat
    orientation = (-1, 2) # east, north
    L, W, Lres, Wres = 500e3, 500e3, x_resolution, y_resolution # dimensions and resolution of grid
    grid = lompe.cs.CSgrid(lompe.cs.CSprojection(position, orientation), L, W, Lres, Wres, R = 6481.2e3)

    # set up conductances and model
    SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, times[0], 'hall'    )
    SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, times[0], 'pedersen')
    model = lompe.Emodel(grid, Hall_Pedersen_conductance = (SH, SP))

    # Collect datasets here
    pfisr_data = pfisr.collect_data(pfisrfn, time_intervals)

    # loop through times and save
    for i, row in time_intervals.iterrows():
        t = row['starttime']
        print("t: ",t)
    
        SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, t, 'hall'    )
        SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, t, 'pedersen')

        model.clear_model(Hall_Pedersen_conductance = (SH, SP)) # reset
    
        # add datasets for this time 
        model.add_data(pfisr_data[i])

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


