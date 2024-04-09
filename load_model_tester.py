#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 23:58:22 2024

@author: clevenger
"""

from lompe.utils.save_load_utils import load_model


file='/Users/clevenger/Projects/data_assimilation/march_19/lompe_outputs/swarm/2023-03-19_063500.nc'
#file = '/Users/clevenger/Projects/lompe_pfisr/isr_3d_vefs_testing/isr_3d_vefs_model_run_outputs/for_dropbox/just_pfisr/02122023/nc_files/2023-02-12_100000.nc'
loaded_model = load_model(file, time='first')

#ve, vn = loaded_model.v(-147, 65) # lon, lat
#ve, vn = loaded_model.v(21.1, 67.9)
#print("ve: ", ve) 
#print("vn: ", vn)

fac = loaded_model.FAC(-147, 65)
#fac = loaded_model.FAC(21.1, 67.9)
print("FAC: ", fac)
fac_all = loaded_model.FAC()
#print("Entire FAC: ", fac_all)

efield = loaded_model.E(-147, 65)
#efield = loaded_model.E(21.1, 67.9)
print("E-Field: ", efield)
efield_all = loaded_model.E()
#print("Entire E-Field: ", efield_all)