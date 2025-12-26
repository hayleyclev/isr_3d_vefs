import pandas as pd
import datetime as dt
import importlib
import os
import pfrr_run_lompe

"""
This is the top-level runscript for isr_3d_vefs
Download data at these locations:
    - swarm cross-track plasma: https://swarm-diss.eo.esa.int/#swarm/Advanced/Plasma_Data/16Hz_TII_Cross-track_Dataset
"""


"""
iweight params & save direc
"""
spreadsheet_path = '/Users/clevenger/Projects/paper01/events/20230227/lompe/inputs/parameters/paper_weights.csv' # spreadsheet with iweights specified (you can make this one input if you only care to have one single lompe run)
df = pd.read_csv(spreadsheet_path)
base_savepath = '/Users/clevenger/Projects/paper01/events/20230227/lompe/outputs/cases/' # save everything here
"""
Set to 'None' for no dataset/excluding existing dataset
"""
#pfisrfn=None
#magfn=None
#superdarn_fn=None
#swarm_a_tii_fn = None
swarm_b_tii_fn = None
swarm_c_tii_fn = None


"""
Set main direcs for where data is located if all in same directory
"""
paper01_direc = '/Users/clevenger/Projects/paper01/sop23_data/202302/27/'

"""
files under specified directory
"""
pfisrfn = paper01_direc + '20230227.002_lp_5min-fitcal.h5'
magfn = paper01_direc + 'SuperMAG_60s_custom_20230227_060000_to_175959_rev-0006.1743653071.csv'
superdarn_fn = paper01_direc + 'superdarn/' # kod vs ksr specified in pfrr_run_lompe script, change there as needed
swarm_a_tii_fn = paper01_direc + 'SW_EXPT_EFIA_TCT02_20230227T042051_20230227T164506_0302.cdf'
#swarm_b_tii_fn = paper01_direc + ''
#swarm_c_tii_fn = paper01_direc + 'SW_EXPT_EFIC_TCT02_20230227T090151_20230227T120406_0302.cdf'

"""
For swarm mags
    - set 'True' for use this satellite
    - set 'None' for NOT use this satellite
"""
swarm_a_prime = True
swarm_b_prime = None
swarm_c_prime = True

"""
Select start and end times for model run
"""
start_time = dt.datetime(2023, 2, 27, 8, 35, 0)
end_time = dt.datetime(2023, 2, 27, 8, 40, 0)

"""
Other tweakable things
"""
time_step = dt.timedelta(minutes=5)
Kp = 6
x_resolution = 10.e3
y_resolution = 10.e3

"""
Run the model given all of the above inputs
"""
df = pd.read_csv(spreadsheet_path)

for idx, row in df.iterrows():
    savepath = os.path.join(base_savepath, str(idx))
    os.makedirs(savepath, exist_ok=True)
    
    pfrr_run_lompe.run_lompe_pfisr(
        start_time, end_time, time_step, Kp, x_resolution, y_resolution,
        swarm_a_prime=swarm_a_prime,
        swarm_b_prime=swarm_b_prime,
        swarm_c_prime=swarm_c_prime,
        plot_save_outdir=savepath,
        nc_save_outdir=savepath,
        pfisrfn=pfisrfn,
        pokermagfn=magfn,
        superdarn_direc=superdarn_fn,
        swarm_a_tii_fn=swarm_a_tii_fn,
        swarm_b_tii_fn=swarm_b_tii_fn,
        swarm_c_tii_fn=swarm_c_tii_fn,
        pfisr_weight=row['pfisr'],
        superdarn_weight=row['sd_kod'],
        mag_weight=row['super_mag'],
        swarm_mag_weight=row['swarm_mag'],
        swarm_tii_weight=row['swarm_tii'],
        swarm_a_efi_fn=None # replacing with tii handlers
    )
