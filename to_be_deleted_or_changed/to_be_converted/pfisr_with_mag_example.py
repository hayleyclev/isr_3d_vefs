#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 12:12:24 2023

@author: clevenger
"""

from lompe_pfisr_mag_demo import run_lompe_pfisr

conductance_functions = True

savepath = '/Users/clevenger/Projects/lompe_pfisr/isr_3d_vefs_testing/isr_3d_vefs_model_run_outputs/' 
pfisrfn = '/Users/clevenger/Projects/lompe_pfisr/test_datasets/20170616.001_lp_1min-fitcal.h5'
pokermagfn = '/Users/clevenger/Projects/lompe_pfisr/mag_data/poker_mag/06162017/csv_ins/poker_2017_06_16_14.csv'


start_time = '2017-06-16 14:00'
end_time = '2017-06-16 14:59'
freq = '5Min'
time_step = 5 * 60
Kp = 1
x_resolution = 50.e3
y_resolution = 50.e3




#ouput = run_lompe_pfisr(parameters)
# radar coordinates, grid dimensions, kept hard-coded as this is PFISR specific for now
run_lompe_pfisr(start_time, end_time, freq, time_step, Kp, x_resolution,
                y_resolution, pfisrfn, 
                savepath, savepath, pokermagfn)
    # model.run_inversion creates the nc's (inside of lompe.model)
    # plots made from last step of lompe_pfisr_demo.py and are saved
    # to whatever input directory is