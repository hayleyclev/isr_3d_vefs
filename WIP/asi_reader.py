import os
import glob
import datetime as dt
import xarray as xr

def read_asi(event, hemi='north', tempfile_path='./'):
    """
    Called and used for modelling auroral conductance in cmodel.py

    Extract the relevant ASI info from ASI spectral inversion method (github.com/hclev/asispectralinversion)
    Will load all ASI data from specified hemisphere into xarray object

    Parameters
    ----------
    event : str
        string on format 'yyyy-mm-dd' to specify time of event for model
    hemi : str, optional
        specify hemisphere 
        Default: 'north'
    tempfile_path : str, optional
        Location for storing processed SSUSI data.
        Default: './'

    Returns
    -------
    savefile : str
        Path to saved file containing asispectralinversion data + conductances extracted from the images

    """
    if not tempfile_path.endswith('/'):
        tempfile_path += '/'

    # Check if the processed file exists
    savefile = tempfile_path + event.replace('-', '') + '_conductivity_' + hemi + '.nc'
    if os.path.isfile(savefile):
        return savefile

    try:
        import h5py
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            'read_asi: Could not load h5py module. Will not be able to read HDF5 files from ASI output folder.')

    # Assuming processed files are in tempfile_path and follow a specific pattern
    files = glob.glob(tempfile_path + '*' + event.replace('-', '') + '*.h5')
    files.sort()

    if len(files) == 0:
        print('No HDF5 files found.')
        return None

    imgs = []  # List to hold all images. Converted to xarray later.

    for file in files:
        with h5py.File(file, 'r') as f:
            # Pull in conductance, location, and time information
            gdlat = f['Geodetic Latitude'][:] 
            gdlon = f['Geodetic Longitude'][:]
            SP = f['SigP'][:]
            SH = f['SigH'][:]

            # Extract timestamp from filename
            basename = os.path.basename(file)
            timestamp_str = basename.split('.')[0]  # remove file extension
            timestamp_str = timestamp_str.split('_')[1]  # get HHMMSS part
            date_str = basename.split('_')[0]  # get YYYYMMDD part

            # Convert timestamp to datetime
            dtime = dt.datetime.strptime(date_str + '_' + timestamp_str, '%Y%m%d_%H%M%S')
            
            # Create xarray Dataset from h5s
            img = xr.Dataset({
                'latitude': (['row', 'col'], gdlat),
                'longitude': (['row', 'col'], gdlon),
                'SP': (['row', 'col'], SP),
                'SH': (['row', 'col'], SH)
            })
            img = img.expand_dims(date=[dtime])
            imgs.append(img)

    if len(imgs) == 0:
        print('No HDF5 images found.')
        return None

    else: # Save as netCDF in specified path
        imgs = xr.concat(imgs, dim='date')
        imgs = imgs.assign({'hemisphere': hemi})
        imgs = imgs.sortby(imgs['date'])
        print('HDF5 data file saved: ' + savefile)

    imgs.to_netcdf(savefile)

    return savefile
