#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 17:32:38 2024

@author: clevenger
"""

import numpy as np
import matplotlib.pyplot as plt
from lompe.utils.save_load_utils import load_model

# Load the model
file = '/Users/clevenger/Projects/data_assimilation/feb_10/lompe_outputs/just_swarm/swarm_mag/large/b/2023-02-10_110900.nc'
loaded_model = load_model(file, time='first')

# Define the grid of latitude and longitude points centered around (65, -147)
center_lat = 65
center_lon = -147
lat_range = np.arange(center_lat - 10, center_lat + 10.5, 0.5)  # From 55 to 75 with step of 0.5
lon_range = np.arange(center_lon - 10, center_lon + 10.5, 0.5)  # From -157 to -137 with step of 0.5

# Initialize arrays to store the results
efield_magnitude = np.zeros((len(lat_range), len(lon_range)))
dot_product = np.zeros((len(lat_range), len(lon_range)))

# Compute the electric field and dot product for each point
for i, lat in enumerate(lat_range):
    for j, lon in enumerate(lon_range):
        efield = loaded_model.E(lon, lat)
        current_density = loaded_model.j(lon, lat)
        
        # Ensure efield and current_density are 1D arrays
        efield = np.squeeze(efield)
        current_density = np.squeeze(current_density)
        
        efield_magnitude[i, j] = np.linalg.norm(efield)
        
        if efield.shape == current_density.shape:
            dot_product[i, j] = np.dot(current_density, efield)  # j dot E
        else:
            dot_product[i, j] = np.nan  # Handle shape mismatch with NaN

# Plot Electric Field Magnitude without Cartopy
plt.figure(figsize=(14, 10))
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.pcolormesh(lon_range, lat_range, efield_magnitude, shading='auto', cmap='viridis')
plt.colorbar(label='Electric Field (V/m)')
plt.tight_layout()
plt.show()

# Plot Dot Product without Cartopy
plt.figure(figsize=(10, 5))
plt.title('Dot Product of Current Density and Electric Field')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.pcolormesh(lon_range, lat_range, dot_product, shading='auto', cmap='viridis')
plt.colorbar(label='Dot Product (A/m^2 * V/m)')
plt.tight_layout()
plt.show()



