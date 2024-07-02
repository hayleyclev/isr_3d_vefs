import datetime as dt
import pandas as pd
import lompe

"""
Parameters In: 
--------------
    - SuperMAG file path containing magnetometer data
    - Time interval (given in pfrr_run_lompe)
    
Parameters Out:
---------------
    - Handled SuperMAG data, prepared and ready to go into the collect_data function
    
"""

def collect_data(supermagfn, time_intervals):

    # Read in mag data
    mag_data = pd.read_csv(supermagfn)
    mag_data['time'] = pd.to_datetime(mag_data['Date_UTC'], format='%Y-%m-%dT%H:%M:%S') # Starting with datetime object (pulled from csv)
    mag_data['unix_time'] = (mag_data['time'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s') # Converting to unix time

    supermag_data = list()

    for i, (t0, t1) in enumerate(time_intervals):
        
        # Find magnetometer data that falls within the current ISR data chunk time range
        t0_unix = (t0-dt.datetime.utcfromtimestamp(0)).total_seconds()
        t1_unix = (t1-dt.datetime.utcfromtimestamp(0)).total_seconds()
       
        # Pull mag data from desired time range in unix time
        mag_data_DT = mag_data[(mag_data['unix_time'] >= t0_unix) & (mag_data['unix_time'] < t1_unix)]
       
      
        # Create magnetic field object
        #B = mag_data_DT[['dbn_nez', 'dbe_nez', 'dbz_nez']].values.T * 1e-9 # Convert to nanoesla from Tesla
        B = mag_data_DT[['dbe_nez', 'dbn_nez', 'dbz_nez']].values.T * 1e-9 # supermag given in nT, lompe needs Tesla so convert to Tesla
        #B = np.tile(B, (mag_data_DT.shape[0], 1)).T
        print("B Shape: ", B.shape) # should be (3, N)
       
        # Create coordinates array for the magnetometer data
        coords_mag = mag_data_DT[['GEOLON', 'GEOLAT']].values.T # Duplicate lon and lat for each time point
        print("Mag Coords Shape: ", coords_mag.shape) # Should be (2, N)
      
        
        # Create Lompe data object for the magnetometer data
        supermag_data.append(lompe.Data(B, coords_mag, datatype='ground_mag', error=10e-9, iweight=0.4))


    # Return the prepared data
    return supermag_data


