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
#import swarm_a_efi_datahandler as aefi
#import swarm_efi_handler as aefi
import swarm_a_tii_datahandler as atii
import swarm_c_tii_datahandler as ctii
from lompe.utils import conductance
import xarray as xr
import glob
import datetime as dt

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

def run_lompe_pfisr(start_time, end_time, time_step, Kp, x_resolution, y_resolution, pfisr_weight, superdarn_weight, mag_weight, swarm_mag_weight, swarm_tii_weight,
                    swarm_a_prime=None, swarm_b_prime=None, swarm_c_prime=None,
                    plot_save_outdir=None, nc_save_outdir=None, pfisrfn=None, pokermagfn=None, superdarn_direc=None, swarm_a_tii_fn=None, swarm_c_tii_fn=None, swarm_a_efi_fn=None):
#def run_lompe_pfisr(start_time, end_time, time_step, Kp, x_resolution, y_resolution, savefile, swarm_a_prime=None, swarm_b_prime=None, swarm_c_prime=None,
                    #plot_save_outdir=None, nc_save_outdir=None, pfisrfn=None, pokermagfn=None, superdarn_direc=None):

    time0 = [start_time+time_step*i for i in range(int((end_time-start_time)/time_step))]
    time1 = [t0+time_step for t0 in time0]
    time_intervals = np.array([time0, time1]).T

    apex = apexpy.Apex(start_time, refh = 110)

    # Set up grid
    position = (-147, 65) # lon, lat
    orientation = (-1, 2) # east, north
    L, W, Lres, Wres = 500e3, 500e3, x_resolution, y_resolution # dimensions and resolution of grid
    grid = lompe.cs.CSgrid(lompe.cs.CSprojection(position, orientation), L, W, Lres, Wres, R = 6481.2e3)
    
    #savefile = read_asi(start_time=start_time, end_time=end_time, hemi='north', tempfile_path='./')
    
    # pull in savefile from cmodel2, otherwise use Hardy
    #if savefile:
        #asi = xr.open_dataset(savefile)
        #SH = asi.hall
        #SP = asi.pedersen
    #else:
        #SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, time_intervals[0], 'hall'    )
        #SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, time_intervals[0], 'pedersen')


    SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, time_intervals[0], 'hall'    )
    SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, time_intervals[0], 'pedersen')

    # Set up conductances and model
    #SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, time_intervals[0], 'hall'    )
    #SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, time_intervals[0], 'pedersen')
    #cmod = Cmodel(grid, event, time, EUV=True, basepath=basepath, tempfile_path=tempfile_path)
    #asi = read_asi(grid, event, time, tempfile_path=tempfile_path)
    #asi = read_asi(event, hemi='North', tempfile_path=tempfile_path)
    #SH = cmod.hall
    #SP = cmod.pedersen
    #SH = asi.hall
    #SP = asi.pedersen
    model = lompe.Emodel(grid, Hall_Pedersen_conductance = (SH, SP))

    # Collect datasets here
    if pfisrfn:
        pfisr_data = pfisr.collect_data(pfisrfn, time_intervals, iweight=pfisr_weight)
        
    if pokermagfn:
        mag_data = mag.collect_data(pokermagfn, time_intervals, iweight=mag_weight)
        
    if superdarn_direc:
        superdarn_kod_data = sd.collect_data(superdarn_direc, time_intervals, 'kod/', iweight=superdarn_weight) # for now, only one superdarn site at a time
        #superdarn_ksr_data = sd.collect_data(superdarn_direc, time_intervals, 'ksr/')
        
    swarm_a_mag_data = amag.collect_data(start_time, end_time, time_step, iweight=swarm_mag_weight) if swarm_a_prime else None
    swarm_b_mag_data = bmag.collect_data(start_time, end_time, time_step, iweight=swarm_mag_weight) if swarm_b_prime else None
    swarm_c_mag_data = cmag.collect_data(start_time, end_time, time_step, iweight=swarm_mag_weight) if swarm_c_prime else None
    
    #if swarm_a_tii_fn:
        #swarm_a_tii_data = atii.collect_data(swarm_a_tii_fn, start_time, end_time, time_step, iweight=swarm_tii_weight)
    if swarm_a_tii_fn:
        swarm_a_tii_data = atii.collect_data(swarm_a_tii_fn, start_time, end_time, time_step, swarm_tii_weight)
    if swarm_c_tii_fn:
        swarm_c_tii_data = ctii.collect_data(swarm_c_tii_fn, start_time, end_time, time_step, swarm_tii_weight)
        
    
    #print(f"Length of swarm_a_tii_data: {len(swarm_a_tii_data)}")
    #print(f"Length of time_intervals: {len(time_intervals)}")


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
            #model.add_data(swarm_a_tii_data[i])
        if swarm_b_prime:
            model.add_data(swarm_b_mag_data[i])
        if swarm_c_prime:
            model.add_data(swarm_c_mag_data[i])
            #model.add_data(swarm_c_tii_data[i])
        if swarm_a_tii_fn:
            model.add_data(swarm_a_tii_data[i])
        if swarm_c_tii_fn:
            model.add_data(swarm_c_tii_data[i])
            
            


        # Run model
        #gtg, ltl = model.run_inversion(l1 = 1, l2 = 0.1)
        #gtg, ltl = model.run_inversion(l1 = 1, l2 = 0.1, l3 = 0.1, FAC_reg=False)
        gtg, ltl = model.run_inversion(l1=1, l2=0.1, l3=0.1, FAC_reg=False)

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

        
