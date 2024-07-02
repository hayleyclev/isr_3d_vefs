import numpy as np
import apexpy
import lompe
from lompe.utils.conductance import hardy_EUV
from lompe.utils.save_load_utils import save_model
import os
import pfisr_datahandler as pfisr
import mag_datahandler as mag
import swarm_a_mag_datahandler as amag
import swarm_b_mag_datahandler as bmag
import swarm_c_mag_datahandler as cmag
import superdarn_datahandler as sd

"""
Tweakable Parameters:
---------------------
    - Apex reference height
    - Geodetic latitude and longitudinal position
    - Eastward and Northward offset/orientation
    - Model space length [km]
    - Model space width [km]
    - Earth's radius
    - Lambda 1 & 2 (regularization parameters)

Purpose:
--------
    - Collects all data sets that have been run through their respective data handlers
    - Standardizes timing across all data sets
    - Performs Lompe model inversion
    - Creates and saves PNG plots and netCDF formatted files of model output data
    
"""

def run_lompe_pfisr(start_time, end_time, time_step, Kp, x_resolution, y_resolution, swarm_a_prime=None, swarm_b_prime=None, swarm_c_prime=None,
                    plot_save_outdir=None, nc_save_outdir=None, pfisrfn=None, pokermagfn=None, superdarn_direc=None):

    time0 = [start_time+time_step*i for i in range(int((end_time-start_time)/time_step))]
    time1 = [t0+time_step for t0 in time0]
    time_intervals = np.array([time0, time1]).T

    apex = apexpy.Apex(start_time, refh = 110)

    # Set up grid
    position = (-147, 65) # lon, lat
    orientation = (-1, 2) # east, north
    L, W, Lres, Wres = 500e3, 500e3, x_resolution, y_resolution # dimensions and resolution of grid
    grid = lompe.cs.CSgrid(lompe.cs.CSprojection(position, orientation), L, W, Lres, Wres, R = 6481.2e3)

    # Set up conductances and model
    SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, time_intervals[0], 'hall'    )
    SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, time_intervals[0], 'pedersen')
    model = lompe.Emodel(grid, Hall_Pedersen_conductance = (SH, SP))

    # Collect datasets here
    if pfisrfn:
        pfisr_data = pfisr.collect_data(pfisrfn, time_intervals)
        
    if pokermagfn:
        mag_data = mag.collect_data(pokermagfn, time_intervals)
        
    if superdarn_direc:
        superdarn_kod_data = sd.collect_data(superdarn_direc, time_intervals, 'kod/') # for now, only one superdarn site at a time
        #superdarn_ksr_data = sd.collect_data(superdarn_direc, time_intervals, 'ksr/')
        
    swarm_a_mag_data = amag.collect_data(start_time, end_time, time_step) if swarm_a_prime else None
    swarm_b_mag_data = bmag.collect_data(start_time, end_time, time_step) if swarm_b_prime else None
    swarm_c_mag_data = cmag.collect_data(start_time, end_time, time_step) if swarm_c_prime else None

    # Loop through times and save
    for i, (stime, etime) in enumerate(time_intervals):
        t = stime
        print("t: ",t)
    
        SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, t, 'hall'    )
        SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, t, 'pedersen')

        model.clear_model(Hall_Pedersen_conductance = (SH, SP)) # reset
    
        # Add datasets for this time
        if pfisrfn:
            model.add_data(pfisr_data[i])
        if pokermagfn:
            model.add_data(mag_data[i])
        if superdarn_direc:
            model.add_data(superdarn_kod_data[i])
            #model.add_data(superdarn_ksr_data[i])
        if swarm_a_prime:
            model.add_data(swarm_a_mag_data[i])
        if swarm_b_prime:
            model.add_data(swarm_b_mag_data[i])
        if swarm_c_prime:
            model.add_data(swarm_c_mag_data[i])

        # Run model
        gtg, ltl = model.run_inversion(l1 = 2, l2 = 0.1)
    

        # Save default model plots
        savefile = os.path.join(plot_save_outdir,str(t).replace(' ','_').replace(':',''))
        print(savefile)
        lompe.lompeplot(model, include_data = True, time = t, apex = apex, savekw = {'fname': savefile, 'dpi' : 200})

        # Save model netCDF files
        savefile = os.path.join(nc_save_outdir,str(t).replace(' ','_').replace(':','')+'.nc') # create directory to save output as nc to read in
        print("@@@@@####$$#$#@: ", model.data.keys())
        for dtype in model.data.keys():
            print("DTYPE", dtype)
            for ds in model.data[dtype]:
                print([ds.coords[key] for key in ['lon', 'lat']])
                
        
        save_model(model, file_name=savefile) # one file per time stamp
        