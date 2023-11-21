import numpy as np
import pandas as pd
# import datetime
from datetime import timedelta
from lompe.utils.conductance import hardy_EUV
import apexpy
import lompe
import matplotlib.pyplot as plt
import h5py
from lompe.utils.save_load_utils import save_model
plt.ioff()


def run_lompe_pfisr(start_time, end_time, freq, time_step, Kp, x_resolution, y_resolution, pfisrfn,
                    plot_save_outdir, nc_save_outdir):


    # times during entire day
    times = pd.date_range(start_time, end_time, freq=freq) # no data in some minutes - figure that out
    # DT currently doesn't matter - only selecting 1 timestamp based on t0
    DT = timedelta(seconds = time_step) # will select data from +- DT

    apex = apexpy.Apex(times[0], refh = 110)

    # set up grid
    position = (-147, 65) # lon, lat
    orientation = (-1, 2) # east, north
    L, W, Lres, Wres = 500e3, 500e3, x_resolution, y_resolution # dimensions and resolution of grid
    grid = lompe.cs.CSgrid(lompe.cs.CSprojection(position, orientation), L, W, Lres, Wres, R = 6481.2e3)

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

    # get figures from entire day and save somewhere


    SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, times[0], 'hall'    )
    SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, times[0], 'pedersen')
    model = lompe.Emodel(grid, Hall_Pedersen_conductance = (SH, SP))

    # loop through times and save
    for t in times[:]:
        print("t: ",t)
    
        SH = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, t, 'hall'    )
        SP = lambda lon = grid.lon, lat = grid.lat: hardy_EUV(lon, lat, Kp, t, 'pedersen')

        model.clear_model(Hall_Pedersen_conductance = (SH, SP)) # reset
    
        pfisr_data = prepare_data(ke, kn, kz, Vlos, glat, glon, galt, Midtime, t, t + DT)
    
        model.add_data(pfisr_data)

        gtg, ltl = model.run_inversion(l1 = 2, l2 = 0.1)
    
        #vvels_fn='/Users/clevenger/Projects/lompe_pfisr/vvels_in/20170616.001_lp_1min-fitcal-vvels_lat.h5'
        #vvels_in=pickle.dump(model, vvels_fn)

        # USE FOR SAVING MODEL PLOTS
        savefile = plot_save_outdir + str(t).replace(' ','_').replace(':','')
        lompe.lompeplot(model, include_data = True, time = t, apex = apex, savekw = {'fname': savefile, 'dpi' : 200})

        # USE FOR SAVING MODEL NCs
        savefile = nc_save_outdir + str(t).replace(' ','_').replace(':','')+'.nc' # create directory to save output as nc to read in
        save_model(model, file_name=savefile) # one file per time stamp
        
        # pathlib; os.path for filenames/outdirs

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


    
    
