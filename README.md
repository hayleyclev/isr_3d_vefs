# isr_3d_vefs
This repository is a host for scripts used to resolve vector electric fields (VEFs) from incoherent scatter radar (ISR) data.

This code uses the Lompe model (https://github.com/klaundal/lompe) to generate two-dimensional (geodetic latitude and geodetic longitude) electrodynamic reconstructions of the plasma velocity flow field and current system in the local region of Poker Flat.  These reconstructions can be used for a variety of scientific investigations, or to drive a physics-based model such as GEMINI (https://github.com/gemini3d). 

The following figure describes what data can be taken in and what information can be reconstructed.  Please note that not all inputs are required (all reconstructions can be performed with a single data input), however, the higher the data density, the more physically realistic the reconstruction.

<img width="792" alt="image" src="https://github.com/hayleyclev/isr_3d_vefs/assets/114105668/6cd6d70f-ca63-4307-87a1-f46158351968">

## Instructions for Running

1. Download the necessary dependencies (many are conda installable; all are pip installable):
   - pip
     ```
     conda install pip
     ```
   - lompe
     ```
     pip install lompe
     ```
   - apexpy
     ```
     pip install apexpy
     ```
   - matplotlib
     ```
     conda install matplotlib
     ```
   - numpy
     ```
     conda install numpy
     ```
   - pandas
     ```
     conda install pandas
     ```
   - scipy
     ```
     conda install scipy
     ```
   - xarray
     ```
     conda install xarray
     ```
   - ppigrf
     ```
     pip install ppigrf
     ```
   - astropy
     ```
     pip install astropy
     ```
   - cdflib
     ```
     conda install cdflib
     ```
   - madrigalWeb
     ```
     pip install madrigalWeb
     ```
   - netCDF4
     ```
     conda install netCDF4
     ```
   - pyAMPS
     ```
     pip install pyAMPS
     ```
   - pydarn
     ```
     pip install pydarn
     ```
   - datetime
     ```
     conda install datetime
     ```
   - h5py
     ```
     conda install h5py
     ```
   - os
     ```
     conda install os
     ```
   - math
     ```
     conda install math
     ```
   - glob
     ```
     conda install glob
     ```
   - viresclient
     ```
     pip install viresclient
     ```
   - cartopy
     ```
     pip install cartopy
     ``` 

2. Download appropriate data.  These may include:
- PFISR (hdf5)
- SuperDARN (fitacf)
- SuperMAG (csv)
- Swarm (viresclient request; see Step 3)

3. If you plan to use Swarm data, create a viresclient token:
After installing viresclient, continue to https://viresclient.readthedocs.io/en/latest/installation.html and follow the steps to create a viresclient token.  Save this token and have it ready to type/paste every time you run the top-level script for every instance of pulling Swarm data.

4. Either open the isr_3d_vefs/pfrr_runscript.py file, or set up your own run script using the following template:

```
from pfrr_run_lompe import run_lompe_pfisr
import datetime as dt

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
```

The specified files should contain data for the time period specified.  If a data file is not provided for a particular instrument (set relevnat filename variable to 'None'), Lompe will automatically run without using that input. Additional user inputs at the top-level include Kp (for conductivity calculation) and resolution for both dimensions.  Output summary plots and netcdf files that contain the lompe model outputs will be saved to the output directory, one for each time step.

5. Run this script, whether it is the direct isr_3d_vefs/pfrr_runscript.py (with your file paths and specifications) or your equivalent modified version using the template described in step 4.  Depending on the number of time steps and data avialable, it may take a few seconds to several minutes.

## Example Run with Real Data

An example run can be performed using isr_3d_vefs/pfrr_runscript.py and data that can be accessed at https://www.dropbox.com/scl/fo/cd3k4x3vft5xpcbj99nyp/AA4By_Jw7cZPFfWzd6WLzSY?rlkey=2tlyd5eq45ibes7fgeloovra1&st=vdc2cen1&dl=0.

After accessing the link, you will see several files and folders containing data from various sources located at or near Poker Flat, AK for an event taking place on February 12, 2023. Download each of these files.  Here is a brief description of what each of these files/folders are:
  - 20230212.002_lp_5min-fitcal.h5 is the PFISR data file, as downloaded from https://amisr.com/amisr/links/data-access/
  - 20240317-21-01-supermag.csv is the SuperMAG data file, as downloaded from https://supermag.jhuapl.edu/mag/?fidelity=low&start=2023-02-12T06%3A00%3A00.000Z&interval=20%3A00&stations=SIT,DED,DAW,BRW,FYU,EAG,CMO,PKR,SHU,JCO,T39,T41,T55
  - kod and ksr are folders containing SuperDARN data; this data was obtained directly from a SuperDARN PI
  - 20230212.002_lp_1min-fitcal-vvels_lat.h5 is a processed version of the PFISR data, which was obtained by performing the Resolved Vector Velocities ("vvels") method (https://ljlamarche.github.io/amisr_user_manual/new_vvels.html#plot-vectors-on-map); this is used to compare results of plasma flows and electric fields from the Lompe run with another method as a sanity check.

Once the data has been downloaded, copy the file paths of your saved data into the appropriate filename variables in isr_3d_vefs/pfrr_runscript.py.  Run this script.  After a few seconds, if you chose "True" for any of the Swarm optional inputs, you should be prompted to input your viresclient token.  You will be prompted to input your token for each "True" marked for the Swarm inputs.  Once those have been entered, the data handling, inverting, and plotting of the data will take place.  After the script has completed its run, check the file path you entered as your output directory.  There should be several nc and png files.  If that is the case, your run has successfully completed.

The nc files can be opened and checked either directly using the output_testing_tools/load_model_tester.py or by setting up a script using the following template:
```
from lompe.utils.save_load_utils import load_model

file='/your_file_path_to_model_outputs/2023-02-12_064500.nc'
loaded_model = load_model(file, time='first')

ve, vn = loaded_model.v(-147, 65) # lon, lat
print("ve: ", ve) 
print("vn: ", vn)

fac = loaded_model.FAC(-147, 65)
print("FAC: ", fac)

fac_all = loaded_model.FAC()
print("FAC shape: ", fac_all.shape)

efield = loaded_model.E(-147, 65)
print("E-Field: ", efield)
```

See https://github.com/klaundal/lompe/blob/main/lompe/model/model.py to determine how to call each model object.

Additionally, you can compare your Lompe model outputs to vvels using output_testing_tools/lompe_velocity_vvels_comp_tool.py.  Similarly to the isr_3d_vefs main script, you will need to input the file paths from the downloaded data files.  You will need to change the value "67" in lines 28 and 29 to match the time pulled from the vvels file to the time of your Lompe output file.

## Notes for Users
As with any open source code, this code is free for anyone to clone, fork, etc to make changes to and use however you please. But as a general note, here is how the code is structured so that you can have a clear idea as to "what goes where" for any changes you may need to make for your own use.  The code is broken into four main groups:
1. Top-Level
   This is isr_3d_vefs/pfrr_runscript.py.  Here is where you determine base-level options like which types of data to use that you have available,       event dates and times, time step, Kp, and resolution.
2. Mid-Level
   This is isr_3d_vefs/pfrr_run_lompe.py.  Here is where you can determine more parameters, such as the area of interest (it is currently set over       Poker Flat, AK so this is how you could change it to another high-latitude area), regularization parameters, and more. I would highly recommend       reading the Local Mapping of Polar Ionospheric Electrodynamics paper [Laundal et. al 2022]
   (https://agupubs.onlinelibrary.wiley.com/doi/epdf/10.1029/2022JA030356) before making changes to these variables, especially to the regularization
   parameters.
4. Low-Level
   This includes isr_3d_vefs/mag_datahandler.py, isr_3d_vefs/pfisr_datahandler.py, isr_3d_vefs/superdarn_datahandler.py,
   isr_3d_vefs/swarm_a_mag_datahandler.py, isr_3d_vefs/swarm_b_mag_datahandler.py, and isr_3d_vefs/swarm_c_mag_datahandler.py.  As you may have
   noticed, each of these are termed as data handlers. Each of these scripts perform any work that must be done to format the input data in a way 
   that Lompe can perform its inversion process. The only parameter that can be tweaked here without breaking the script architecture is the
   iweight factor within each of these respective data handlers. Prior to changing these, I would again recommend reading the Laundal et. al 2022 
   paper.
6. Post-Processing
   These are output_testing_tools/load_model_tester.py and output_testing_tools/lompe_velocity_vvelds_comp_tool.py.  These are left as a means of
   testing your outputs to ensure everything works as expected.


## Contact Information
For any bugs found, issues in running the code, or questions please feel free to create a GitHub issue or contact me (Hayley Clevenger) directly at clevenh1@my.erau.edu.

