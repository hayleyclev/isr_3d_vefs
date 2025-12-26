import numpy as np
import datetime as dt
import lompe
import h5py

"""
Parameters In: 
--------------
    - PFISR long-pulse experiment file path (given in top-level)
    - Time interval (given in pfrr_run_lompe)
    
Parameters Out:
---------------
    - Handled PFISR data, prepared and ready to go into the collect_data function
    
"""

def collect_data(pfisrfn, time_intervals, iweight):

    # read in datafile
    with h5py.File(pfisrfn,"r") as h5:
        # O+ indexing - error could come about if -1 used instead of 0
        # beam_codes = h5['BeamCodes'][:,0]
        # print(beam_codes[:,0])
   
        Vlos = h5['FittedParams/Fits'][:,:,:,0,3]
        Vlos[np.abs(Vlos)>1000.] = np.nan
    
        glat = h5['Geomag/Latitude'][:]
        glon = h5['Geomag/Longitude'][:]
        galt = h5['Geomag/Altitude'][:]
        utime = h5['Time/UnixTime'][:]
        unix_Midtime = np.mean(utime, axis=1)
    
        ke = h5['Geomag/ke'][:]
        kn = h5['Geomag/kn'][:]
        kz = h5['Geomag/kz'][:]

    pfisr_data = list()

    # collect lompe Data object for each time interval
    for i, (stime, etime) in enumerate(time_intervals):

        unix_stime = (stime-dt.datetime.utcfromtimestamp(0)).total_seconds()
        unix_etime = (etime-dt.datetime.utcfromtimestamp(0)).total_seconds()
        
        pfisr_data.append(prepare_data(ke, kn, kz, Vlos, glat, glon, galt, unix_Midtime, unix_stime, unix_etime, iweight))

    return pfisr_data

# These files contain entire AMISR experiment. Function to select from a smaller time interval is needed:
def prepare_data(ke, kn, kz, Vlos, glat, glon, galt, Midtime, t0, t1, iweight):
    """ get data from correct time period """

    Tidx1 = np.argmin(np.abs(Midtime[:] - t0)) # will need Tidx1 AND Tidx2
    Tidx2 = np.argmin(np.abs(Midtime[:] - t1)) # number of beams x number of bins - 

    print('Vlos', Vlos[Tidx1:Tidx2, :, :].shape) 
    
    glat_new = np.tile(glat, (Tidx2 - Tidx1, 1, 1)) # expanded, to flatten later
    glon_new = np.tile(glon, (Tidx2 - Tidx1, 1, 1)) # expanded, to flatten later
    
    print("glat shape: ", glat.shape)
    print("glat (tile'd') shape:" , glat_new.shape)
    print("glon shape: ", glon.shape)
    print("glon (tile'd') shape:" , glon_new.shape)
    coords = np.array([glon_new.flatten(), glat_new.flatten()])
    print("coords shape: ", coords.shape)
    
    
    vlos_input = Vlos[Tidx1:Tidx2, :, :] # no beams x no records x no bins - will need to flatten beams&time
    print("vlos input shape: ",vlos_input.shape)
    # estimate parallel velocity here instead of finding theta - FAV=0, no LOS diff
    cos_theta_input = (np.sqrt(ke**2+kn**2)/(np.sqrt(ke**2+kn**2+kz**2)))
    print('cos theta shape: ',cos_theta_input.shape)
    vlos=(vlos_input/cos_theta_input).flatten()
    vlos[np.abs(vlos)>5000.] = np.nan #quick fix for vertical, FA beams
    # beam filtering - scaling vertical components - uncertainties
    print("vlos shape: ",vlos.shape)
    # print("vlos used for calculations: ", vlos)
    
    ke_norm = ke/np.sqrt(ke**2+kn**2)
    kn_norm = kn/np.sqrt(ke**2+kn**2)
    ke_norm_new = np.tile(ke_norm, (Tidx2 - Tidx1, 1, 1)) # expand out to later flatten
    kn_norm_new = np.tile(kn_norm, (Tidx2 - Tidx1, 1, 1)) # expand out to later flatten
    
    print("ke_norm shape: ",ke_norm.shape)
    print("kn_norm shape: ",kn_norm.shape)
    print("ke_norm shape: ",ke_norm_new.shape)
    print("kn_norm shape: ",kn_norm_new.shape)
    
    los = np.array([ke_norm_new.flatten(), kn_norm_new.flatten()])
    print("los shape: ",los.shape)
    
    pfisr_data = lompe.Data(vlos, coordinates = coords, LOS = los, datatype = 'convection', scale = None, iweight=iweight) # vlos - no time records x no beams  no range gates 
    # duplicate for coords and los - use np.tile() to do this - flatten to keep shape
    #print("prepared vlos: ", vlos)
    #print("prepared los: ", los)
    
    return pfisr_data
