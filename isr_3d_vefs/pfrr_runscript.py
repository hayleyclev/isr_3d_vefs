from pfrr_run_lompe import run_lompe_pfisr
import datetime as dt

# save your viresclient token here for easy copy/paste access

"""
Inputs:
-------
    - Folder location to save model output files
    - PFISR file location (set to None if not available)
    - SuperMAG file location (set to None if not available)
    - SuperDARN filename (set to None if not available)
    - Swarm A/B/C (set to True if using, set to None if not)
    - Experiment/event start time
    - Experiment/event end time
    - Time step
    - Kp
    - Resolution (x and y) [km]

Purpose:
--------
    - Collects all input files and routes them to their respective data handlers
    - Pressing F5/Run File takes you all of the way to the end
     (check your savepath to ensure the files have been created)
     
Notes:
------
    - The example here and provided data within the repository are for:
        - February 12, 2023
        - Over Poker Flat, Alaska
        - As a part of the Swarm-over-Poker 2023 (SoP23) campaign
    
"""

savepath = '/Users/clevenger/Projects/paper01/events/20230227/lompe_weighting_test/12/'
pfisrfn = '/Users/clevenger/Projects/paper01/sop23_data/202302/27/20230227.002_lp_5min-fitcal.h5'
#pfisrfn = None
magfn = '/Users/clevenger/Projects/paper01/sop23_data/202302/27/SuperMAG_60s_custom_20230227_060000_to_175959_rev-0006.1743653071.csv'
superdarn_fn = '/Users/clevenger/Projects/superDARN/test_data/fitacf_30/kod/2023/202302/20230227/' # this folder should contain SD data grouped by STATION ID
#superdarn_fn = None
#swarm_a_efi_fn = '/Users/clevenger/Projects/AGU24/event_data/20230214/swarm_efi/a/SW_EXPT_EFIA_TCT02_20230214T030751_20230214T153406_0302.cdf'
swarm_a_efi_fn = None
swarm_a_prime = True
swarm_b_prime = None
swarm_c_prime = True
#tempfile_path = '/Users/clevenger/Projects/AGU24/derived_data/20230214/asi_inversion/9UT/outputs/gemini_remapped/'

start_time = dt.datetime(2023, 2, 27, 8, 20, 0)
end_time = dt.datetime(2023, 2, 27, 8, 50, 0)
time_step = dt.timedelta(minutes=5)
Kp = 6
x_resolution = 10.e3
y_resolution = 10.e3

run_lompe_pfisr(start_time, end_time, time_step, Kp, x_resolution,
                y_resolution, swarm_a_prime, swarm_b_prime, swarm_c_prime, plot_save_outdir=savepath, nc_save_outdir=savepath,
                pfisrfn=pfisrfn, pokermagfn=magfn, superdarn_direc=superdarn_fn, swarm_a_efi_fn=swarm_a_efi_fn)
