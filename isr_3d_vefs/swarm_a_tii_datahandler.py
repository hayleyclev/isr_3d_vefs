import numpy as np
import lompe
import pandas as pd
import cdflib


def collect_data(swarm_a_tii_fn, start_time, end_time, time_step, iweight):

    # Load CDF
    v = cdflib.CDF(swarm_a_tii_fn)
    
    # Convert all timestamps to datetime objects
    swarm_time = cdflib.epochs.CDFepoch.to_datetime(v.varget('Timestamp'))
    
    # Read in variables from CDF
    qf = v.varget('Quality_flags')
    viz = v.varget('Viz').astype(float)
    viy = v.varget('Viy').astype(float)
    latitude = v.varget('Latitude').astype(float)
    longitude = v.varget('Longitude').astype(float)
    vsat_n = v.varget('VsatN').astype(float)
    vsat_e = v.varget('VsatE').astype(float)
    
    # Mask bad (flagged) data
    viz[qf < 1] = np.nan
    viy[qf < 1] = np.nan
    
    # Create a DataFrame for time filtering and time chunking
    df = pd.DataFrame({
        'Time': swarm_time,
        'Latitude': latitude,
        'Longitude': longitude,
        'Viz': viz,
        'Viy': viy,
        'VsatN': vsat_n,
        'VsatE': vsat_e
    }).set_index('Time')
    
    # Filter out times we don't care about
    df = df[(df.index >= start_time) & (df.index <= end_time)]
    
    # Loop through all relevant times within start/end time in time step cadence
    swarm_a_tii_data = []
    current_time = start_time
    while current_time <= end_time:
        next_time = current_time + time_step
        chunk_df = df[(df.index >= current_time) & (df.index < next_time)]
    
        if chunk_df.empty:
            print(f"Skipping empty chunk: {current_time} to {next_time}")
            current_time = next_time
            continue
    
        print(f"Processing chunk: {current_time} to {next_time}")
    
        coords = np.vstack((chunk_df['Longitude'].values, chunk_df['Latitude'].values))
        vlos = np.vstack((chunk_df['Viy'].values, chunk_df['Viz'].values))
        los_e = chunk_df['VsatE'].values
        los_n = chunk_df['VsatN'].values
    
        # Normalize LOS vectors
        magnitude = np.sqrt(los_e**2 + los_n**2)
        los_e_norm = los_e / magnitude
        los_n_norm = los_n / magnitude
        LOS = np.vstack((los_e_norm, los_n_norm))
    
        tii_data = lompe.Data(
            vlos,
            coordinates=coords,
            LOS=LOS,
            datatype='convection',
            scale=None,
            iweight=iweight
        )
    
        swarm_a_tii_data.append(tii_data)
        current_time = next_time

    return swarm_a_tii_data