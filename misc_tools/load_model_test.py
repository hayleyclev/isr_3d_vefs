#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 11:36:09 2023

@author: clevenger
"""

from lompe.utils.save_load_utils import load_model


file='/Users/clevenger/Projects/lompe_pfisr/lompe_output_xarray_test.nc'
loaded_model = load_model(file, time='first')

ve, vn = loaded_model.v(-147, 65) # lon, lat
print("ve: ", ve) 
print("vn: ", vn)
