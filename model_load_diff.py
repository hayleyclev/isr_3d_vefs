#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 23:48:39 2024

@author: clevenger
"""

from lompe.utils.save_load_utils import load_model
import numpy as np
import matplotlib.pyplot as plt
from lompe.model import Emodel


file='/Users/clevenger/Projects/data_assimilation/feb_12/lompe_outputs/509_runs/pfisr_supermag/large/nc_files/2023-02-12_103000.nc'
file2 = '/Users/clevenger/Projects/data_assimilation/feb_12/lompe_outputs/509_runs/pfisr_supermag/pfisr_fov/nc_files/2023-02-12_103000.nc'
#file = '/Users/clevenger/Projects/lompe_pfisr/isr_3d_vefs_testing/isr_3d_vefs_model_run_outputs/for_dropbox/just_pfisr/02122023/nc_files/2023-02-12_100000.nc'
loaded_model = load_model(file, time='first')
loaded_model2 = load_model(file2, time='first')

lat = loaded_model.lat_J
lon = loaded_model.lon_J

lat2 = loaded_model2.lat_J
lon2 = loaded_model2.lon_J

#ve, vn = loaded_model.v() # lon, lat
#ve, vn = loaded_model.v(-147, 65)
ve, vn = loaded_model.v()
max_ve = np.max(ve)
max_vn = np.max(vn)
#print("ve: ", ve) 
#print("vn: ", vn)
print("ve: ", max_ve)
print("vn: ", max_vn)

#ve2, vn2 = loaded_model2.v(-147, 65)
ve2, vn2 = loaded_model2.v()
max_ve2 = np.max(ve2)
max_vn2 = np.max(vn2)
#print("ve2: ", ve2) 
#print("vn2: ", vn2)
print("ve 2: ", max_ve2)
print("vn 2: ", max_vn2)

#diff_ve = np.abs(ve2 - ve)
diff_ve = np.abs(max_ve2 - max_ve)
print("ve difference: ", diff_ve)

#diff_vn = np.abs(vn2 - vn)
diff_vn = np.abs(max_vn2 - max_vn)
print("vn difference: ", diff_vn)

print("lat shape: ", lat.shape)
print("lon shape: ", lon.shape)
print("lat2 shape: ", lat2.shape)
print("lon2 shape: ", lon2.shape)
print("ve shape: ", ve.shape)
print("vn shape: ", vn.shape)
print("ve2 shape: ", ve2.shape)
print("vn2 shape: ", vn2.shape)

plt.scatter(lat, lon)
plt.scatter(lat2, lon2)
plt.show()

#fac = loaded_model.FAC()
#fac = loaded_model.FAC(-147, 65)
fac = loaded_model.FAC()
max_fac = np.max(fac)
#print("FAC: ", fac)
print("FAC: ", max_fac)
#fac_all = loaded_model.FAC()
#print("Entire FAC: ", fac_all)
#fac2 = loaded_model2.FAC(-147, 65)
fac2 = loaded_model2.FAC()
max_fac2 = np.max(fac2)
#print("FAC2: ", fac2)
print("FAC2: ", max_fac2)

#diff_fac = np.abs(fac2 - fac)
diff_fac = np.abs(max_fac2 - max_fac)
print("fac difference: ", diff_fac)

#plt.plot(fac)
#plt.plot(fac2)
#plt.show()

#efield = loaded_model.E()
#efield = loaded_model.E(-147, 65)
efield = loaded_model.E()
max_efield = np.max(efield)
#print("efield: ", efield)
print("efield: ", max_efield)
#efield2 = loaded_model2.E(-147, 65)
efield2 = loaded_model2.E()
max_efield2 = np.max(efield2)
#print("efield 2: ", efield2)
print("efield 2: ", max_efield2)

#diff_efield = np.abs(efield2[1,:] - efield[1,:])
diff_efield = np.abs(max_efield2[1,:] - max_efield[1,:])
print("efield difference, comp1: ", diff_efield)

#diff_efield = np.abs(efield2[:,1] - efield[:,1])
diff_efield = np.abs(max_efield2[:,1] - max_efield[:,1])
print("efield difference, comp 2: ", diff_efield)
#print("E-Field: ", efield)
#efield_all = loaded_model.E()
#print("Entire E-Field: ", efield_all)

#ve, vn = loaded_model.v(-147, 65)
#print("ve: ", ve)
#print("vn: ", vn)

