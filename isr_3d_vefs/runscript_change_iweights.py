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
spreadsheet_path = '/Users/clevenger/Downloads/tii_weight_test.csv'
df = pd.read_csv(spreadsheet_path)
base_savepath = '/Users/clevenger/Projects/paper01/events/20230208/lompe/14_kod/'

"""
Set to 'None' for no dataset/excluding existing dataset
"""
pfisrfn=None
magfn=None
#superdarn_fn=None
swarm_a_tii_fn = None
swarm_b_tii_fn = None
swarm_c_tii_fn = None


"""
Set main direcs for where data is located if all in same directory
"""
paper01_direc = '/Users/clevenger/Projects/paper01/sop23_data/202302/12/'
#sd_direc = '/Users/clevenger/Projects/paper01/sop23_data/202302/08/superdarn/'
#sd_station = 'kod/' # and also set which SD station 'kod/' or 'ksr/'

"""
20230227 files
"""
#pfisrfn = paper01_direc + '20230227.002_lp_5min-fitcal.h5'
#magfn = paper01_direc + 'SuperMAG_60s_custom_20230227_060000_to_175959_rev-0006.1743653071.csv'
#superdarn_fn = sd_direc + sd_station + '2023/202302/20230227/'
#swarm_a_tii_fn = paper01_direc + 'SW_EXPT_EFIA_TCT02_20230227T042051_20230227T164506_0302.cdf'
#swarm_b_tii_fn = paper01_direc + ''
#swarm_c_tii_fn = paper01_direc + 'SW_EXPT_EFIC_TCT02_20230227T090151_20230227T120406_0302.cdf'

"""
20230208 files
"""
#pfisrfn = paper01_direc + '20230208.001_lp_5min-fitcal.h5'
#magfn = paper01_direc + 'SuperMAG_60s_custom_20230208_060000_to_175959_rev'
#superdarn_fn = sd_direc + sd_station + '2023/202302/20230208/'
#swarm_a_tii_fn = ''
#swarm_b_tii_fn = paper01_direc + 'SW_EXPT_EFIB_TCT16_20230208T050251_20230208T173507_0401.cdf'
#swarm_c_tii_fn = ''

"""
20230210 SD trial
"""
#superdarn_fn = sd_direc + sd_station + '2023/202302/20230212/'
superdarn_fn = '/Users/clevenger/Projects/paper01/sop23_data/202302/27/superdarn/'

"""
For swarm mags
    - set 'True' for use this satellite
    - set 'None' for NOT use this satellite
"""
swarm_a_prime = None
swarm_b_prime = None
swarm_c_prime = None

"""
Select start and end times for model run
"""
start_time = dt.datetime(2023, 2, 27, 8, 30, 0)
end_time = dt.datetime(2023, 2, 27, 9, 30, 0)
#start_time = dt.datetime(2023, 2, 8, 10, 0, 0)
#end_time = dt.datetime(2023, 2, 8, 11, 0, 0)
#start_time = dt.datetime(2023, 2, 14, 9, 10, 0)
#end_time = dt.datetime(2023, 2, 14, 9, 30, 0)

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
