from sandbox_pfrr_run_lompe import run_lompe_pfisr
import datetime as dt

savepath = '/Users/clevenger/Projects/lompe_pfisr/isr_3d_vefs_testing/restructure-branch/no_mag/' 
pfisrfn = '/Users/clevenger/Projects/lompe_pfisr/test_datasets/pfisr/06162017/20170616.001_lp_1min-fitcal.h5'
magfn = '/Users/clevenger/Projects/lompe_pfisr/test_datasets/supermag/06162017/20170616_supermag.csv'

start_time = dt.datetime(2017, 6, 16, 14, 0, 0)
end_time = dt.datetime(2017, 6, 16, 14, 59, 59)
time_step = dt.timedelta(minutes=5)
Kp = 1
x_resolution = 50.e3
y_resolution = 50.e3

run_lompe_pfisr(start_time, end_time, time_step, Kp, x_resolution,
                y_resolution, plot_save_outdir = savepath, nc_save_outdir=savepath,
                pfisrfn=pfisrfn, pokermagfn=magfn)

