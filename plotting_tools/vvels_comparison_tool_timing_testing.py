import numpy as np
import h5py
import datetime as dt
import os
import re
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr
from lompe.utils.save_load_utils import load_model

def find_closest_time(file_times, target_time):
    if isinstance(target_time, dt.datetime):
        target_time = np.array([target_time])
    time_diffs = np.abs(np.array(file_times)[:, np.newaxis] - target_time)
    return np.argmin(time_diffs, axis=0)


# HDF5 file
vvels_fn = '/Users/clevenger/Projects/vvels/by_date/06162017/20170616.001_lp_1min-fitcal-vvels_lat.h5'

# set target time
target_time = np.array([dt.datetime(2017, 6, 16, 14, 00)])  # Set your target time as a NumPy array

with h5py.File(vvels_fn, "r") as h5:
    alt = h5["VvelsGeoCoords/Altitude"][:, 0]
    alt_ind = np.argmin(np.abs(alt - 300))
    lat = h5["VvelsGeoCoords/Latitude"][alt_ind, :]
    lon = h5["VvelsGeoCoords/Longitude"][alt_ind, :]

    # find target time in h5
    time_values = h5['Time/UnixTime'][:]
    target_index = find_closest_time(time_values, target_time)

    vel = h5["VvelsGeoCoords/Velocity"][target_index, alt_ind, :, :-1]
    utime = time_values[target_index]

print("HDF5 Target Time:", dt.datetime.utcfromtimestamp(utime).strftime('%Y-%m-%d %H:%M:%S'))

# NetCDF files
nc_folder = '/Users/clevenger/Projects/lompe_pfisr/isr_3d_vefs_testing/isr_3d_vefs_model_run_outputs/for_vvels_comp_06162017'

# List all netCDF files in the folder
nc_files = [f for f in os.listdir(nc_folder) if f.endswith(".nc")]

# Extract timestamps from filenames and convert to datetime objects
nc_times = [re.search(r'(\d{4}-\d{2}-\d{2}_\d{6})\.nc', f).group(1) for f in nc_files]
nc_times = [dt.datetime.strptime(time_str, '%Y-%m-%d_%H%M%S') for time_str in nc_times]

# Find the closest timestamp in netCDF files
nc_target_index = find_closest_time(np.array(nc_times), target_time)
nc_target_file = nc_files[nc_target_index]

print("NetCDF Target Time:", nc_times[nc_target_index])

# Load the Lompe model from the netCDF file
nc_target_path = os.path.join(nc_folder, nc_target_file)
model = load_model(nc_target_path)

# Retrieve velocity information from the Lompe model for the specified location
lompe_ve, lompe_vn = model.v(lat, lon)

print("Lompe Model Target Time:", model.time)

def scale_uv(lon, lat, u, v):
    # scaling/rotation of vector to plot in cartopy
    us = u / np.cos(lat * np.pi / 180.)
    vs = v
    sf = np.sqrt(u ** 2 + v ** 2) / np.sqrt(us ** 2 + vs ** 2)
    return us * sf, vs * sf

plt.rcParams.update({'font.size': 12})
fig = plt.figure()
proj = ccrs.Orthographic(central_longitude=-147.0, central_latitude=65.0)  # change lat, lon

ax_map = fig.add_subplot(111, projection=proj)
gl = ax_map.gridlines(color='dimgrey', draw_labels=True)
ax_map.coastlines(linewidth=0.5)
ax_map.add_feature(cfeature.LAND, color='whitesmoke')
ax_map.add_feature(cfeature.OCEAN, color='white')
ax_map.set_extent([-150, -140, 65, 68], crs=ccrs.PlateCarree())

s = 150

u, v = scale_uv(lon, lat, vel[:, 0], vel[:, 1])
Q = ax_map.quiver(lon, lat, u, v, zorder=5, scale=100, color='green', transform=ccrs.PlateCarree())

u, v = scale_uv(lon, lat, lompe_ve, lompe_vn)
Q = ax_map.quiver(lon, lat, u, v, zorder=5, scale=100, color='red', transform=ccrs.PlateCarree())

ax_map.quiverkey(Q, 0.4, 0.2, 0.1, 'E=100mV/m', labelpos='E', transform=ax_map.transAxes)
ax_map.legend()

plt.savefig('dce_map.png')
plt.show()

