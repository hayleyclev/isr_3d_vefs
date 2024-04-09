#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 22:50:40 2024

@author: clevenger
"""

from TEST_pfrr_run_lompe import run_lompe_pfisr
import datetime as dt

# vOzoHzs61RJYFjDTizvm0TPWu6JC_WIp

savepath = '/Users/clevenger/Projects/data_assimilation/feb_12/lompe_outputs/509_runs/just_pfisr/large/' 
pfisrfn = '/Users/clevenger/Projects/data_assimilation/feb_12/input_data/PFISR/themis36/data/lp/20230212.002_lp_5min-fitcal.h5'
#magfn = '/Users/clevenger/Projects/data_assimilation/feb_12/input_data/SuperMAG/20240317-21-01-supermag.csv'
magfn = None

start_time = dt.datetime(2023, 2, 12, 11, 55, 0)
end_time = dt.datetime(2023, 2, 12, 12, 15, 0)
time_step = dt.timedelta(minutes=5)
Kp = 2
x_resolution = 50.e3
y_resolution = 50.e3

run_lompe_pfisr(start_time, end_time, time_step, Kp, x_resolution,
                y_resolution, plot_save_outdir = savepath, nc_save_outdir=savepath,
                pfisrfn=pfisrfn, pokermagfn=magfn)

#run_lompe_pfisr(start_time, end_time, time_step, Kp, x_resolution,
                #y_resolution, plot_save_outdir = savepath, nc_save_outdir=savepath,
                #pfisrfn=pfisrfn, pokermagfn=magfn, include_swarm_mag_a=True, 
                #include_swarm_mag_b=True, include_swarm_mag_c=True