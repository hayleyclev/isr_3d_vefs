import numpy as np
import datetime as dt
import lompe
import h5py
import numpy as np
import cdflib
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import cartopy.crs as ccrs

"""
Parameters In: 
--------------
    - SWARM A EFI data file path (given in top-level)
    - Time interval (given in pfrr_run_lompe)
    
Parameters Out:
---------------
    - Handled SWARM A EFI_TCT data, prepared and ready to go into the collect_data function
    
"""

def collect_data(swarm_a_efi_fn, start_time, end_time, time_intervals):

    v = cdflib.CDF(swarm_a_efi_fn)
    
    starttime = np.datetime64(start_time)
    endtime = np.datetime64(end_time)

    swarm_time = cdflib.epochs.CDFepoch.to_datetime(v.varget('Timestamp'))
    #swarm_utime = swarm_time.astype(int)

    # Find indices for time range
    stidx = np.argmin(np.abs(starttime-swarm_time))
    etidx = np.argmin(np.abs(endtime-swarm_time))

    swarm_time = swarm_time[stidx:etidx+1]
    #swarm_utime = swarm_time.astype('datetime64[s]').astype(int)
    #swarm_utime = swarm_utime[stidx:etidx]

    # Quality flags
    qf = v.varget('Quality_flags', startrec=stidx, endrec=etidx)
    cf = v.varget('Calibration_flags', startrec=stidx, endrec=etidx)

    # Read velocities
    Vixh = v.varget('Vixh', startrec=stidx, endrec=etidx)
    Vixv = v.varget('Vixv', startrec=stidx, endrec=etidx)
    Viy = v.varget('Viy', startrec=stidx, endrec=etidx)
    Viz = v.varget('Viz', startrec=stidx, endrec=etidx)

    # Filter flagged data
    Vixh[qf<1] = np.nan
    Vixv[qf<1] = np.nan
    Viy[qf<1] = np.nan
    Viz[qf<1] = np.nan

    # Read satelite position and velocity
    swarm_glat = v.varget('Latitude', startrec=stidx, endrec=etidx)
    swarm_glon = v.varget('Longitude', startrec=stidx, endrec=etidx)
    r = v.varget('Radius', startrec=stidx, endrec=etidx)
    swarm_galt = r/1000. - 6371.
    VsatN = v.varget('VsatN', startrec=stidx, endrec=etidx)
    VsatE = v.varget('VsatE', startrec=stidx, endrec=etidx)
    VsatC = v.varget('VsatC', startrec=stidx, endrec=etidx)


    swarm_a_efi_data = list()

    # collect lompe Data object for each time interval
    for i, (stime, etime) in enumerate(time_intervals):

        unix_stime = (stime-dt.datetime.utcfromtimestamp(0)).total_seconds()
        unix_etime = (etime-dt.datetime.utcfromtimestamp(0)).total_seconds()
        
        swarm_a_efi_data.append(prepare_data(VsatN, VsatE, VsatC, Vixh, Vixv, Viy, Viz))

    return swarm_a_efi_data

# These files contain entire AMISR experiment. Function to select from a smaller time interval is needed:
def prepare_data(VsatN, VsatE, VsatC, Vixh, Vixv, Viy, Viz):
    """ get data from correct time period """

    Vsat_mag = np.sqrt(VsatN**2 + VsatE**2 + VsatC**2)
    VsN = VsatN/Vsat_mag
    VsE = VsatE/Vsat_mag
    VsC = VsatE/Vsat_mag

    # Calculate velocity vectors in ENU coordinates
    s = VsatC.shape
    #R = np.array([[VsE, -VsN, np.zeros(s)],
    #              [VsN, VsE, np.zeros(s)],
    #              [-VsC, np.zeros(s), np.ones(s)]]).transpose((2,0,1))
    R = np.array([[VsE, VsN, -VsC*VsE],
                  [VsN, -VsE, -VsC*VsN],
                  [-VsC, np.zeros(s), VsC**2-1]]).transpose((2,0,1))
    Vi = np.array([(Vixh+Vixv)/2., Viy, Viz]).T
    Vi_2d = np.array([(Vixh+Vixv)/2., Viy]).T
    swarm_vel = np.einsum('...ij,...j->...i', R, Vi)
    swarm_vel_2d = np.einsum('...ij,...j->...i', R, Vi_2d)
    swarm_vel_mag = np.linalg.norm(Vi[:,:2], axis=1)
    swarm_vel_mag_2d = np.linalg.norm(Vi_2d[:,:2], axis=1)
    print(Vi.shape, swarm_vel_mag.shape)
    
    vlos = swarm_vel_2d.T
    print("swarm efi vlos shape: ", vlos.shape)
    los = swarm_vel_mag_2d.T
    print("swarm efi los shape: ", los.shape)
    coords = Vi_2d.T
    print("swarm efi coords shape: ", coords.shape)
    print("swarm efi R shape: ", R.shape)
    
    swarm_a_efi_data = lompe.Data(vlos, coords, LOS = los, datatype = 'convection', scale = None)
    
    return swarm_a_efi_data