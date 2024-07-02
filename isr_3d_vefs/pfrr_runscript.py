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

savepath = '/your_save_path_here/' 
pfisrfn = '/your_file_path_here/20230212.002_lp_5min-fitcal.h5'
magfn = '/your_file_path_here/20240317-21-01-supermag.csv'
superdarn_fn = '/your_file_path_here/<name of superdarn file location>/' # this folder should contain SD data grouped by STATION ID
swarm_a_prime = True
swarm_b_prime = None
swarm_c_prime = True


start_time = dt.datetime(2023, 2, 12, 6, 30, 0)
end_time = dt.datetime(2023, 2, 12, 8, 30, 0)
time_step = dt.timedelta(minutes=5)
Kp = 2
x_resolution = 50.e3
y_resolution = 50.e3

run_lompe_pfisr(start_time, end_time, time_step, Kp, x_resolution,
                y_resolution, swarm_a_prime, swarm_b_prime, swarm_c_prime, plot_save_outdir=savepath, nc_save_outdir=savepath,
                pfisrfn=pfisrfn, pokermagfn=magfn, superdarn_direc=superdarn_fn)