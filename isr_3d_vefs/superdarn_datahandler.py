import math
import pydarn
import datetime as dt
import numpy as np
from lompe.data_tools.dataloader import los_azimuth2en
from pydarn.utils.coordinates import gate2geographic_location
import glob
import lompe
import lompe.model

"""
Parameters In: 
--------------
    - SuperDARN file path, with files separated by SD STATION ID (given in top-level)
    - Radar Station ID (given in pfrr_run_lompe)
    
Parameters Out:
---------------
    - Handled SuperDARN data FOR A SINGLE STATION, prepared and ready to go into the collect_data function
    
"""
    
def collect_data(fitacf_dir, time_intervals, radar_id):
    fitacf_files = glob.glob(f"{fitacf_dir}/{radar_id}/*")

    """
    For a list of strings containing fitACF files, return the input parameters needed for lompe
    Going forward, grid files would be much quicker, but for now this works better with 3 second
    wide beam data

    Parameters
    ----------
    fitacf_dir : str
        String of the directory containing the fitACF files
    fitacf_files : list[str] or str
        List of strings or single string containing fitACF file names
    time_of_interest : dt.datetime or list[dt.datetime]
        Time or list of times of interest
    DT : dt.timedelta
        Amount of time from time_of_interest to include

    Returns
    -------
    vlos
        tbd
    coords
        tbd
    los
        tbd
    """
    # Set up numpy arrays that will hold the important parameters
    glon = [np.empty((0,))]*len(time_intervals)
    glat = [np.empty((0,))]*len(time_intervals)
    vlos = [np.empty((0,))]*len(time_intervals)
    vlos_err = [np.empty((0,))]*len(time_intervals)
    le = [np.empty((0,))]*len(time_intervals)
    ln = [np.empty((0,))]*len(time_intervals)
    
    print("vlos length: ", len(vlos)) 
    print("time_intervals length: ", len(time_intervals))
    
    print("fitacf_files: ", fitacf_files)

        
    for fitacf_file in fitacf_files:
        
        print("start reading file: ", fitacf_file)
        
        # Read in the fitACF data
        sdarn_read = pydarn.SuperDARNRead(fitacf_file)
        fitacf_data = sdarn_read.read_fitacf()
        print("???? num of records????: ", len(fitacf_data))
        
            
        # Station ID
        stid = fitacf_data[0]['stid']
            
        # Find the relevant times
        record_times = [dt.datetime(fitacf_data[x]['time.yr'], fitacf_data[x]['time.mo'], fitacf_data[x]['time.dy'],
                                    fitacf_data[x]['time.hr'], fitacf_data[x]['time.mt'], fitacf_data[x]['time.sc'],
                                    fitacf_data[x]['time.us']) for x in range(0, len(fitacf_data))]
        
        unix_record_times = np.array([(t0-dt.datetime.utcfromtimestamp(0)).total_seconds() for t0 in record_times])
            
        # Find the times which are within time_of_interest+DT
        for n, (t0, t1) in enumerate(time_intervals):
            
            t0_unix = (t0-dt.datetime.utcfromtimestamp(0)).total_seconds()
            t1_unix = (t1-dt.datetime.utcfromtimestamp(0)).total_seconds()
            
            #radar_data_DT = radar_data[(record_times >= t0_unix) & (record_times < t1_unix)]
            #print("timing stuff:", (t0_unix <= unix_record_times) & (unix_record_times <= t1_unix))
            chunk_indices = np.argwhere((t0_unix <= unix_record_times) & (unix_record_times <= t1_unix))
            chunk_indices = np.squeeze(chunk_indices)
            #print("chunk indices: ", chunk_indices)
            
            print("length of fitacf_data:", len(fitacf_data))
            
            for i in chunk_indices:
                
                print(fitacf_data[i].keys())
                slist = fitacf_data[i]['slist']
                gflg = fitacf_data[i]['gflg'] 

                # Range seperation and frang
                try:
                    rsep = fitacf_data[i]['rsep']
                except KeyError:
                    rsep = 45

                # Distance to first range gate
                try:
                    frang = fitacf_data[i]['frang']
                except KeyError:
                    frang = 180

                # The current beam
                beam = fitacf_data[i]['bmnum']
                
                # Iterate over the gates
                for j, gate in enumerate(slist):
                    # Only continue if not ground scatter, velocity is below 2000m/s, and range gates above 10
                    # This removes most erroneous data and near-range (E-region) echos
                    if gflg[j] == 0 and abs(fitacf_data[i]['v'][j]) <= 2000 and gate > 10:
                        # Get coordinates of this beam/gate
                        lat, lon = gate2geographic_location(stid=stid, beam=beam, range_gate=gate, height=300,
                                                            center=True, rsep=rsep, frang=frang)

                        # Kvectors aren't in fitACF files, so we need to calculate it ourselves
                        azm = fitacf_get_k_vector(stid, lat, lon, fitacf_data[i]['v'][j])

                        # Get the unit vectors in east and west directions
                        le_current, ln_current = los_azimuth2en(azm)

                        # Append to placeholder arrays
                        glat[n] = np.append(glat[n], lat)
                        glon[n] = np.append(glon[n], lon)

                        # Needs to be magnitude of the velocity, sign is handled by azimuth
                        vlos[n] = np.append(vlos[n], abs(fitacf_data[i]['v'][j]))
                        vlos_err[n] = np.append(vlos_err[n], abs(fitacf_data[i]['v_e'][j]))
                        le[n] = np.append(le[n], le_current)
                        ln[n] = np.append(ln[n], ln_current)
                    else:
                        #print('No slist found in this record')
                        continue
        print('Done file: ' + fitacf_file)
    
    superdarn_data = []
    
    for n in range(len(time_intervals)):
        vlos0 = np.array(vlos[n])
        print("time intervals: ", time_intervals[n])
        print("vlos0 shape: ", vlos0.shape)
        vlos_err0 = np.array(vlos_err[n])
        coords0 = np.vstack((glon[n], glat[n]))
        #coords0 = np.vstack((glat[n], glon[n]))
        print("coords0 shape: ", coords0.shape)
        los0 = np.vstack((le[n], ln[n]))
        #los0 = np.vstack((ln[n], le[n]))
        print("los0 shape: ", los0.shape)
    
        superdarn_data.append(lompe.Data(vlos0, coordinates = coords0, LOS = los0, datatype = 'convection', scale = None, iweight=1.0))

    return superdarn_data


def fitacf_get_k_vector(stid, lat, lon, v_los):
    """
    Calculate the magnetic azimuth (k-vector) of the line-of-sight velocity component
    for the given radar

    Parameters
    ----------
    stid : int
        Station ID of the radar
    lat : float
        Latitiude of the measured velocity
    lon : float
        Longitude of the measured velocity
    v_los : float
        Line-of-sight velocity at this position, positive away from the radar

    Returns
    -------
    kvect : float
        Angle of the vector from the geographic pole, in degrees
    """

    # Get position of radar in geographic from hdw files in pyDARN
    radlat = pydarn.SuperDARNRadars.radars[stid].hardware_info.geographic.lat
    radlon = pydarn.SuperDARNRadars.radars[stid].hardware_info.geographic.lon

    # Convert points to cartesian
    vec_start_x = (90 - lat) * np.cos(np.radians(lon))
    vec_start_y = (90 - lat) * np.sin(np.radians(lon))
    radlat_x = (90 - radlat) * np.cos(np.radians(radlon))
    radlat_y = (90 - radlat) * np.sin(np.radians(radlon))

    # Get the angle between the radar location and the current coordinate
    theta = math.atan2(radlat_x - vec_start_x, radlat_y - vec_start_y)

    # Resolve the LOS velocity into the cartesian frame
    # It only matters if the value is positive or away, so keep numbers simple (debugging)
    if v_los >= 1:
        vsign = 5
    else:
        vsign = -5
    vec = [(vsign * np.sin(theta)), (vsign * np.cos(theta))]

    # Vector that points to the origin (pole)
    origin_vec = [-vec_start_x, -vec_start_y]

    # Now work out the angle between origin_vec and vec, which is the geographic azimuth from north
    atana = math.atan2(vec[0],vec[1])
    atanb = math.atan2(origin_vec[0], origin_vec[1])
    kvect = np.degrees(atana - atanb)

    return kvect