import numpy as np
import h5py
import datetime as dt
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr 
from lompe.utils.save_load_utils import load_model


# vvels file and model save location
vvels_fn = '/your_file_path_to_vvels_file/20230212.002_lp_1min-fitcal-vvels_lat.h5'
save_fn = '/your_file_path_to_model_output/2023-02-12_064500.nc'

# load lompe model (or multiple if doing many comparisons)
model = load_model(save_fn)

# vvels file stuff - pull velocity info
with h5py.File(vvels_fn, "r") as h5:
    # Find index of closest timestamp in vvels file
    utimes = h5['Time/UnixTime'][:]
    # Extract data based on found index
    alt = h5["VvelsGeoCoords/Altitude"][:, 0]
    alt_ind = np.argmin(np.abs(alt - 300))
    lat = h5["VvelsGeoCoords/Latitude"][alt_ind, :]
    lon = h5["VvelsGeoCoords/Longitude"][alt_ind, :]
    
    vel = h5["VvelsGeoCoords/Velocity"][67, alt_ind, :, :-1]
    utime = utimes[67].astype('datetime64[s]')
    print("utime:", utime)

# lompe file stuff - pull velocity info
lompe_ve, lompe_vn = model.v(lon, lat)

print("lompe_ve shape: ", lompe_ve.shape)
print("lompe_vn shape: ", lompe_vn.shape)

def scale_uv(lon, lat, u, v):
    # scaling/rotation of vector to plot in cartopy
    # https://github.com/SciTools/cartopy/issues/1179
    us = u/np.cos(lat*np.pi/180.)
    vs = v
    sf = np.sqrt(u**2+v**2)/np.sqrt(us**2+vs**2)
    return us*sf, vs*sf


plt.rcParams.update({'font.size': 12})
fig = plt.figure()
proj = ccrs.Orthographic(central_longitude=-147.0, central_latitude=65.0) #change lat, lon

ax_map = fig.add_subplot(111, projection=proj)
gl = ax_map.gridlines(color='dimgrey', draw_labels=True)
# gl.top_labels = False
ax_map.coastlines(linewidth=0.5)
ax_map.add_feature(cfeature.LAND, color='whitesmoke')
ax_map.add_feature(cfeature.OCEAN, color='white')
ax_map.set_extent([-150,-140,65,68], crs=ccrs.PlateCarree())

ax_map.set_xlabel('Longitude')
ax_map.set_ylabel('Latitude')


s = 150

#ax_map.plot(lon, lat, linewidth=3, color='red', label='High Flier', transform=ccrs.Geodetic())
u, v = scale_uv(lon, lat, vel[:,0], vel[:,1])
Q = ax_map.quiver(lon, lat, u, v, zorder=5, scale=2000, color='darkorange', transform=ccrs.PlateCarree(), label = 'vvels flows')

u, v = scale_uv(lon, lat, lompe_ve, lompe_vn)
Q = ax_map.quiver(lon, lat, u, v, zorder=5, scale=2000, color='lime', transform=ccrs.PlateCarree(), label = 'Lompe flows')

ax_map.legend(loc='upper left', fontsize='small')

ref_velocity = 1000
#ax_map.quiverkey(Q, 0.4, 0.2, 0.1, ref_velocity, labelpos='E', transform=ax_map.transAxes)
ax_map.legend()
ax_map.legend(loc='lower right', fontsize='small')

plt.savefig('dce_map.png')
plt.show()

# error - diffs, plots
np.set_printoptions(threshold=np.inf)