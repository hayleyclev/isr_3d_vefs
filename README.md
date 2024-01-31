# isr_3d_vefs
Repository for scripts to resolve vector electric fields (VEFs) from incoherent scatter radar (ISR) data.

This code use lompe to generate a reconstruction of the plasma velocity flow field and current system in the local region of Poker Flat.  These reconstructions can be used for a variety of science investigations, or to drive a physics-based model such as GEMINI.

## Instructions for Running

1. Download appropriate data.  These may include:
- PFISR
- SuperDARN
- Swarm
- SuperMAG
Data files should be saved in ...

2. Set up a run script using the following model:

```
from pfrr_run_lompe import run_lompe_pfisr
import datetime as dt

savepath = '/path/to/desired/output/location' 
pfisrfn = '/path/to/pfisr/file'
magfn = '/path/to/supermag/file'

start_time = dt.datetime(2017, 6, 16, 14, 0, 0)
end_time = dt.datetime(2017, 6, 16, 14, 59, 59)
time_step = dt.timedelta(minutes=5)
Kp = 1
x_resolution = 50.e3
y_resolution = 50.e3

run_lompe_pfisr(start_time, end_time, time_step, Kp, x_resolution,
                y_resolution, plot_save_outdir = savepath, nc_save_outdir=savepath,
                pfisrfn=pfisrfn, pokermagfn=magfn)
```

The specified files should contain data for the time period specified.  If a data file is not provided for a particular instrument, lompe will automatically run without using that input.  Output summary plots and netcdf files with that contain the lompe model will be saved to the output directory, one for each time step.

3. Run this script.  Depending on the numbe rof time steps and data avialable, it may take several minutes
