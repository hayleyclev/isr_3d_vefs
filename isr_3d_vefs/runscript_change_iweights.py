import pandas as pd
import datetime as dt
import importlib
import os
import pfrr_run_lompe

# iweight parameter spreadsheet
spreadsheet_path = '/Users/clevenger/Downloads/tii_weight_test.csv'
df = pd.read_csv(spreadsheet_path)

# data inputs
base_savepath = '/Users/clevenger/Projects/paper01/events/20230227/lompe_weighting_test/pfisr_fov/lompe_outputs/20250613_outputs/'
pfisrfn = '/Users/clevenger/Projects/paper01/sop23_data/202302/27/20230227.002_lp_5min-fitcal.h5'
#pfisrfn=None
magfn = '/Users/clevenger/Projects/paper01/sop23_data/202302/27/SuperMAG_60s_custom_20230227_060000_to_175959_rev-0006.1743653071.csv'
#magfn=None
#superdarn_fn = '/Users/clevenger/Projects/superDARN/test_data/fitacf_30/ksr/2023/202302/20230227/'
superdarn_fn=None
swarm_a_tii_fn = '/Users/clevenger/Projects/paper01/sop23_data/202302/27/SW_EXPT_EFIA_TCT02_20230227T042051_20230227T164506_0302.cdf'
#swarm_c_tii_fn = '/Users/clevenger/Projects/paper01/sop23_data/202302/27/SW_EXPT_EFIC_TCT02_20230227T090151_20230227T120406_0302.cdf'
#swarm_a_tii_fn = None
swarm_c_tii_fn = None
#swarm_a_tii_fn = '/Users/clevenger/Projects/paper01/events/20230214/real_data/swarm_EFI_TCT/SW_EXPT_EFIA_TCT02_20230214T030751_20230214T153406_0302.cdf'
swarm_a_prime = True
swarm_b_prime = None
swarm_c_prime = True

start_time = dt.datetime(2023, 2, 27, 8, 0, 0)
#start_time = dt.datetime(2023, 2, 14, 9, 10, 0)
end_time = dt.datetime(2023, 2, 27, 9, 0, 0)
#end_time = dt.datetime(2023, 2, 14, 9, 30, 0)
time_step = dt.timedelta(minutes=5)
Kp = 6
x_resolution = 10.e3
y_resolution = 10.e3

# run
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
        swarm_c_tii_fn=swarm_c_tii_fn,
        pfisr_weight=row['pfisr'],
        superdarn_weight=row['sd_kod'],
        mag_weight=row['super_mag'],
        swarm_mag_weight=row['swarm_mag'],
        swarm_tii_weight=row['swarm_tii'],
        swarm_a_efi_fn=None # replacing with tii handlers
    )
