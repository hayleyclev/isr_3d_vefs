import numpy as np
import pandas as pd
# import datetime
from datetime import timedelta
from lompe.utils.conductance import hardy_EUV
import apexpy
import lompe
import matplotlib.pyplot as plt
import h5py
import os
from lompe.utils.save_load_utils import save_model
plt.ioff()

def collect_data(pfisrfn, time_intervals):

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
        Midtime = np.mean(utime, axis=1)
    
        ke = h5['Geomag/ke'][:]
        kn = h5['Geomag/kn'][:]
        kz = h5['Geomag/kz'][:]

    pfisr_data = list()

    for i, row in time_intervals.iterrows():
        print(i, row)
        
        pfisr_data.append(prepare_data(ke, kn, kz, Vlos, glat, glon, galt, Midtime, row['starttime'], row['endtime']))

    return pfisr_data

# These files contain entire AMISR experiment. Function to select from a smaller time interval is needed:
def prepare_data(ke, kn, kz, Vlos, glat, glon, galt, Midtime, t0, t1):
    """ get data from correct time period """

    Tidx1 = np.argmin(np.abs(Midtime[:] - t0.timestamp())) # will need Tidx1 AND Tidx2
    print("Tidx1: ",Tidx1) 
    print(t0, pd.to_datetime(Midtime[Tidx1], unit='s'))
    Tidx2 = np.argmin(np.abs(Midtime[:] - t1.timestamp())) # number of beams x number of bins - 
    print("Tidx2: ",Tidx2)
    print(t1, pd.to_datetime(Midtime[Tidx2], unit='s'))

    print('Vlos', Vlos[Tidx1:Tidx2, :, :].shape) 
    
    # hard coded for now - make dynamic to time interval later
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
    
    pfisr_data = lompe.Data(vlos, coordinates = coords, LOS = los, datatype = 'convection', scale = None) # vlos - no time records x no beams  no range gates 
    # duplicate for coords and los - use np.tile() to do this - flatten to keep shape
    #print("prepared vlos: ", vlos)
    #print("prepared los: ", los)
    
    return pfisr_data


    
    