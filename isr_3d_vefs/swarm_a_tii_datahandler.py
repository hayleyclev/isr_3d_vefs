import numpy as np
import lompe
import pandas as pd
import cdflib

def collect_data(swarm_a_tii_fn, start_time, end_time, time_step, iweight):
    # Load CDF file
    v = cdflib.CDF(swarm_a_tii_fn)

    # Convert timestamps to datetime
    swarm_time = cdflib.epochs.CDFepoch.to_datetime(v.varget('Timestamp'))

    # Read variables
    qf = v.varget('Quality_flags')
    viz = v.varget('Viz').astype(float)
    viy = v.varget('Viy').astype(float)
    latitude = v.varget('Latitude').astype(float)
    longitude = v.varget('Longitude').astype(float)
    vsat_n = v.varget('VsatN').astype(float)
    vsat_e = v.varget('VsatE').astype(float)

    # Mask bad values
    viz[qf < 1] = np.nan
    viy[qf < 1] = np.nan

    # Create DataFrame indexed by time
    df = pd.DataFrame({
        'Time': swarm_time,
        'Latitude': latitude,
        'Longitude': longitude,
        'Viz': viz,
        'Viy': viy,
        'VsatN': vsat_n,
        'VsatE': vsat_e
    }).set_index('Time')

    # Container for lompe.Data objects per chunk
    swarm_a_tii_data = []

    current_time = start_time
    while current_time <= end_time:
        next_time = current_time + time_step
        chunk_df = df[(df.index >= current_time) & (df.index < next_time)]

        if chunk_df.empty:
            print(f"Skipping empty chunk: {current_time} to {next_time}")
            current_time = next_time
            continue

        print(f"\nProcessing chunk: {current_time} to {next_time}")

        # Prepare coordinates and velocities
        coords = np.vstack((chunk_df['Longitude'].values, chunk_df['Latitude'].values))
        #vlos = np.vstack((chunk_df['Viy'].values, chunk_df['Viz'].values))
        # Compute dot product between velocity vector and LOS unit vector

        # Normalize LOS vectors
        los_e = chunk_df['VsatE'].values
        los_n = chunk_df['VsatN'].values
        magnitude = np.sqrt(los_e**2 + los_n**2)
        magnitude[magnitude == 0] = 1.0  # avoid divide-by-zero
        los_e_norm = los_e / magnitude
        los_n_norm = los_n / magnitude
        los = np.vstack((los_e_norm, los_n_norm))
        
        vlos = chunk_df['Viy'].values * los_n_norm + chunk_df['Viz'].values * los_e_norm
        
        print("swarm a tii los shape: ", los.shape)
        print("swarm a tii vlos shape: ", vlos.shape)
        print("swarm a tii coords shape: ", coords.shape)

        swarm_a_tii_data.append(lompe.Data(vlos, coordinates=coords, LOS=los, datatype='convection', scale=None, iweight=iweight))

        current_time = next_time
        
    return swarm_a_tii_data
