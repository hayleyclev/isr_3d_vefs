#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 20:25:05 2023

@author: clevenger
"""

import xarray as xr
import pandas as pd
from lompe.utils.save_load_utils import load_model

file='/Users/clevenger/Projects/lompe_pfisr/lompe_output_xarray_test.nc'
loaded_model = load_model(file, time='first')

reference_time = pd.to_datetime('2017-06-16 14:00')

loaded_model['timestamp'] = (loaded_model['timestamp'] - reference_time).astype('int')

#ve, vn = loaded_model.v(-147, 65) # lon, lat
vu = xr.DataArray(0, coords = loaded_model.coords, dims = loaded_model.dims)

custom_data = xr.Dataset({'ve': loaded_model['ve'], 'vn': loaded_model['vn'], 'vu': vu})

#nc_file = '/Users/clevenger/Projects/lompe_pfisr/lompe_output_xarray_test.nc'
#data = xr.open_dataset(nc_file)

loaded_model['vu'] = vu

loaded_model = loaded_model[['ve', 'vn', 'vu']]




reshaped_data = loaded_model.to_array().transpose('timestamp', 'altitude', 'bin', 'variable')

array_data = reshaped_data.values

print(array_data)