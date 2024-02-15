import numpy as np
import h5py
import datetime as dt
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr 
from lompe.utils.save_load_utils import load_model

# break into functions that pass in the vvels filename and the lompe model filename
def extract_time_from_filename(filename):
    time_str = filename.split('/')[-1].split('.')[0] 
    return dt.datetime.strptime(time_str, '%Y-%m-%d_%H%M%S')


def find_closest_time(h5, target_time):
    """Finds the index of the closest time to target_time in the HDF5 file."""
    utime = h5['Time/UnixTime'][:]
    times = np.mean(utime, axis=1)  # Assuming the mean of start and end times
    times_dt = np.array([dt.datetime.utcfromtimestamp(t) for t in times])
    closest_idx = np.argmin(np.abs(times_dt - target_time))
    return closest_idx, times_dt[closest_idx]

vvels_fn = '/Users/clevenger/Projects/vvels/by_date/06162017/20170616.001_lp_1min-fitcal-vvels_lat.h5'
save_fn = '/Users/clevenger/Projects/lompe_pfisr/isr_3d_vefs_testing/restructure-branch/no_mag/2017-06-16_145000.nc'

# set target time
target_time = extract_time_from_filename(save_fn)


with h5py.File(vvels_fn,"r") as h5:
    closest_idx, closest_time = find_closest_time(h5, target_time)
    alt=h5["VvelsGeoCoords/Altitude"][:,0]
    print(alt)
    alt_ind = np.argmin(np.abs(alt-300))
    print(alt_ind)
    lat=h5["VvelsGeoCoords/Latitude"][alt_ind, :]
    lon=h5["VvelsGeoCoords/Longitude"][alt_ind, :]
    vel=h5["VvelsGeoCoords/Velocity"][closest_idx, alt_ind, :, :-1] # 50 is made up, change as needed
    utime = h5['Time/UnixTime'][closest_idx] 

print(utime.astype('datetime64[s]'))
    

#print(utime.shape)
print(lat.shape)
print(lon.shape)
print("vel shape: ", vel.shape)

# find target time in lompe nc


model = load_model(save_fn)
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

s = 150

#ax_map.plot(lon, lat, linewidth=3, color='red', label='High Flier', transform=ccrs.Geodetic())
u, v = scale_uv(lon, lat, vel[:,0], vel[:,1])
Q = ax_map.quiver(lon, lat, u, v, zorder=5, scale=2500, color='green', transform=ccrs.PlateCarree())

u, v = scale_uv(lon, lat, lompe_ve, lompe_vn)
Q = ax_map.quiver(lon, lat, u, v, zorder=5, scale=2500, color='red', transform=ccrs.PlateCarree())


# ax_map.plot(LF_data['glon'][::s], LF_data['glat'][::s], linewidth=3, color='blue', label='Low Flier', transform=ccrs.Geodetic())
# u, v = scale_uv(LF_data['glon'][::s], LF_data['glat'][::s], LF_data['EE'][::s], LF_data['EN'][::s])
# Q = ax_map.quiver(LF_data['glon'][::s], LF_data['glat'][::s], u, v, zorder=5, scale=1, linewidth=2, color='green', headlength=0, headwidth=0, headaxislength=0, transform=ccrs.PlateCarree())

ax_map.quiverkey(Q, 0.4, 0.2, 0.1, 'E=100mV/m', labelpos='E', transform=ax_map.transAxes)
ax_map.legend()

plt.savefig('dce_map.png')
plt.show()

# error - diffs, plots
np.set_printoptions(threshold=np.inf)
