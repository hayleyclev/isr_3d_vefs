#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 21:25:44 2024

@author: clevenger
"""

import numpy as np
import apexpy
import lompe
from lompe.utils.conductance import hardy_EUV
from lompe.utils.save_load_utils import save_model
import os
import pfisr_datahandler as pfisr
import mag_datahandler as mag
import TEST_swarm_mag_c_datahandler as cmag
import superdarn_datahandler as sd

def run_lompe_pfisr(start_time, end_time, time_step, Kp, x_resolution, y_resolution,
                    plot_save_outdir=None, nc_save_outdir=None, pfisrfn=None, pokermagfn=None, superdarn_direc=None):

    time0 = [start_time + time_step * i for i in range(int((end_time - start_time) / time_step))]
    time1 = [t0 + time_step for t0 in time0]
    time_intervals = np.array([time0, time1]).T

    apex = apexpy.Apex(start_time, refh=110)
    position = (-147, 65)
    orientation = (-1, 2)
    L, W, Lres, Wres = 500e3, 500e3, x_resolution, y_resolution
    grid = lompe.cs.CSgrid(lompe.cs.CSprojection(position, orientation), L, W, Lres, Wres, R=6481.2e3)

    SH = lambda lon=grid.lon, lat=grid.lat: hardy_EUV(lon, lat, Kp, time_intervals[0], 'hall')
    SP = lambda lon=grid.lon, lat=grid.lat: hardy_EUV(lon, lat, Kp, time_intervals[0], 'pedersen')
    model = lompe.Emodel(grid, Hall_Pedersen_conductance=(SH, SP))

    if pfisrfn:
        pfisr_data = pfisr.collect_data(pfisrfn, time_intervals)
    if pokermagfn:
        mag_data = mag.collect_data(pokermagfn, time_intervals)
    if superdarn_direc:
        superdarn_kod_data = sd.collect_data(superdarn_direc, time_intervals, 'kod/')

    swarm_c_mag_data = cmag.collect_data(start_time, end_time)

    for i, (stime, etime) in enumerate(time_intervals):
        t = stime
        print("Processing time:", t)

        SH = lambda lon=grid.lon, lat=grid.lat: hardy_EUV(lon, lat, Kp, t, 'hall')
        SP = lambda lon=grid.lon, lat=grid.lat: hardy_EUV(lon, lat, Kp, t, 'pedersen')

        model.clear_model(Hall_Pedersen_conductance=(SH, SP))

        if pfisrfn:
            if i < len(pfisr_data):
                print(f"Adding PFISR data for time interval {i}")
                print(f"PFISR data shape: {pfisr_data[i].values.shape}")
                model.add_data(pfisr_data[i])
        if pokermagfn:
            if i < len(mag_data):
                print(f"Adding Magnetometer data for time interval {i}")
                print(f"Magnetometer data shape: {mag_data[i].values.shape}")
                model.add_data(mag_data[i])
        if superdarn_direc:
            if i < len(superdarn_kod_data):
                print(f"Adding SuperDARN data for time interval {i}")
                print(f"SuperDARN data shape: {superdarn_kod_data[i].values.shape}")
                model.add_data(superdarn_kod_data[i])

        if isinstance(swarm_c_mag_data, list):
            if i < len(swarm_c_mag_data):
                print(f"Adding Swarm C magnetic data for time interval {i}")
                if swarm_c_mag_data[i].values.size > 0:
                    print(f"Swarm C data shape: {swarm_c_mag_data[i].values.shape}")
                    model.add_data(swarm_c_mag_data[i])
                else:
                    print(f"No valid Swarm C magnetic data for time interval {i}")
        else:
            print(f"Swarm C magnetic data is not a list, skipping...")

        print("Running inversion...")
        gtg, ltl = model.run_inversion(l1=2, l2=0.1)
        print("Inversion complete.")

        savefile = os.path.join(plot_save_outdir, str(t).replace(' ', '_').replace(':', ''))
        print(f"Saving plot to {savefile}")
        lompe.lompeplot(model, include_data=True, time=t, apex=apex, savekw={'fname': savefile, 'dpi': 200})

        savefile = os.path.join(nc_save_outdir, str(t).replace(' ', '_').replace(':', '') + '.nc')
        print(f"Saving model to {savefile}")
        save_model(model, file_name=savefile)
