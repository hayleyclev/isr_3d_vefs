import math
import pydarn
import datetime as dt
import numpy as np
from lompe.data_tools.dataloader import los_azimuth2en
from pydarn.utils.coordinates import gate2geographic_location
import glob


# fitacf_dir - '\Users\clevenger\Projects\lompe_superdarn\data_inputs\'
# fitacf_files - will be labeled by date
# time_of_interest - dt.datetime(2017, 6, 16)
    # Define the date format in your strings
    # date_format = '%Y-%m-%d %H:%M'
    # Convert the start_time and end_time strings to datetime objects
    # start_time_datetime = datetime.strptime('2023-02-12 08:30', date_format)
    # end_time_datetime = datetime.strptime('2023-02-12 15:00', date_format)
    # time_of_interest = [start_time_datetime, end_time_datetime]
    
def collect_data(fitacf_dir, radar_id, radar_data, record_times):
    fitacf_files = {
        'kod': glob.glob(f"{fitacf_dir}/kod/*.fitacf"),
        'ksr': glob.glob(f"{fitacf_dir}/ksr/*.fitacf")
        }
    
    for i, (t0, t1) in enumerate(time_intervals):
        
        t0_unix = (t0-dt.datetime.utcfromtimestamp(0)).total_seconds()
        t1_unix = (t1-dt.datetime.utcfromtimestamp(0)).total_seconds()
        
        radar_data_DT = radar_data[(record_times >= t0_unix) & (record_times < t1_unix)]
    
        for radar_data in fitacf_files:
            
            superdarn_data = radar_data_chunked[i]
            
            if radar_id is 'kod':
                superdarn_data = fitacf_get_lompe_params(kod_radar_data)
            if radar_id is 'ksr':
                superdarn_data = fitacf_get_lompe_params(ksr_radar_data)
                
            radar_data_chunked[i] = fitacf_get_lompe_params(fitacf_dir, fitacf_files, time_of_interest, DT)
                
        superdarn_kod_data = lompe.Data(vlos, coordinates = coords, LOS = los, datatype = 'convection', scale = None, iweight=1.0)
        superdarn_ksr_data = lompe.Data(vlos, coordinates = coords, LOS = los, datatype = 'convection', scale = None, iweight=1.0)
                
    return superdarn_kod_data, superdarn_ksr_data
                data['vlos'][i]
    


def fitacf_get_lompe_params(fitacf_dir, fitacf_files, time_of_interest, DT):
#def fitacf_get_lompe_params(fitacf_dir, fitacf_files, start_time, end_time, DT):
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

    radar_data = {}
    
    radar_id = {
        'kod',
        'ksr',
        'ade',
        'adw'
        }
    
    for radar_id, file_list in fitacf_files.items():
        # Set up numpy arrays that will hold the important parameters
        glon = []
        glat = []
        vlos = []
        vlos_err = []
        le = []
        ln = []
        
        
        for fitacf_file in file_list:
            # Read in the fitACF data
            sdarn_read = pydarn.SuperDARNRead(fitacf_file)
            fitacf_data = sdarn_read.read_fitacf()
            
            # Station ID
            stid = fitacf_data[0]['stid']
            
            # Find the relevant times
            record_times = [dt.datetime(fitacf_data[x]['time.yr'], fitacf_data[x]['time.mo'], fitacf_data[x]['time.dy'],
                                        fitacf_data[x]['time.hr'], fitacf_data[x]['time.mt'], fitacf_data[x]['time.sc'],
                                        fitacf_data[x]['time.us']) for x in range(0, len(fitacf_data))]
            
            # Find the times which are within time_of_interest+DT
            for i, record_time in enumerate(record_times):
                if DT >= (record_time - time_of_interest) >= dt.timedelta(0):
                    # find which time interval this record is in - chunk into t0 and t1
                    # which interval within the intervals does it fall into0 save the right one to that list and continue the list
                    # list will need to be size of list of all time
                    # save records to index group "0" 
                #if start_time >= record_time <= end_time:
                    # Ranges with data in it, minus ground scatter
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
                            glat = np.append(glat, lat)
                            glon = np.append(glon, lon)

                            # Needs to be magnitude of the velocity, sign is handled by azimuth
                            vlos = np.append(vlos, abs(fitacf_data[i]['v'][j]))
                            vlos_err = np.append(vlos_err, abs(fitacf_data[i]['v_e'][j]))
                            le = np.append(le, le_current)
                            ln = np.append(ln, ln_current)
                    else:
                        print('No slist found in this record')
                        continue
                print('Done file: ' + fitacf_file)

        # Finally, some things into a Lompe format. `vlos` is fine already
        #coords = np.vstack((glon, glat))
        #los = np.vstack((le, ln))
        
        
        radar_data[radar_id] = {
            'vlos': np.array(vlos),
            'vlos_err': np.array(vlos_err),
            'coords': np.vstack((glon, glat)),
            'los': np.vstack((le, ln))
            }

    return radar_data

    
    kod_radar_data = radar_data['kod']
    ksr_radar_data = radar_data['ksr']
    ade_radar_data = radar_data['ade']
    adw_radar_data = radar_data['adw']

    print("kod vlos:", kod_radar_data['vlos'])
    print("ksr vlos:", ksr_radar_data['vlos'])
    print("ade vlos:", ade_radar_data['vlos'])
    print("adw vlos:", adw_radar_data['vlos'])
    



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





