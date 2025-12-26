import cdflib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import argparse

def inspect_tii_file(filename, start_time, end_time, time_step):

    print(f"Loading CDF: {filename}")
    v = cdflib.CDF(filename)

    # Convert timestamps to datetime
    swarm_time = cdflib.epochs.CDFepoch.to_datetime(v.varget('Timestamp'))

    # Read vars
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

    df = pd.DataFrame({
        'Time': swarm_time,
        'Latitude': latitude,
        'Longitude': longitude,
        'Viz': viz,
        'Viy': viy,
        'VsatN': vsat_n,
        'VsatE': vsat_e
    }).set_index('Time')

    df = df[(df.index >= start_time) & (df.index <= end_time)]

    if df.empty:
        print("No data in time range!")
        return

    print(f"\n--- Summary between {start_time} and {end_time} ---")
    print(f"Total rows: {len(df)}")
    print(f"Viz NaNs: {df['Viz'].isna().sum()}, Viy NaNs: {df['Viy'].isna().sum()}")

    print(f"Latitude range: {df['Latitude'].min()} to {df['Latitude'].max()}")
    print(f"Longitude range: {df['Longitude'].min()} to {df['Longitude'].max()}")

    current_time = start_time
    while current_time <= end_time:
        next_time = current_time + time_step
        chunk = df[(df.index >= current_time) & (df.index < next_time)]

        print(f"\n== {current_time} to {next_time} ==")
        print(f"  Samples: {len(chunk)}")
        if chunk.empty:
            current_time = next_time
            continue

        print(f"  Valid Viz: {np.sum(~np.isnan(chunk['Viz']))}, Viy: {np.sum(~np.isnan(chunk['Viy']))}")

        los_e = chunk['VsatE'].values
        los_n = chunk['VsatN'].values
        magnitude = np.sqrt(los_e**2 + los_n**2)

        zero_mag_count = np.sum(magnitude == 0)
        if zero_mag_count > 0:
            print(f"  WARNING: {zero_mag_count} LOS vectors have zero magnitude")

        current_time = next_time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect Swarm TII data in a CDF file")
    parser.add_argument("filename", type=str, help="Path to Swarm A TII .cdf file")
    parser.add_argument("start", type=str, help="Start time (YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("end", type=str, help="End time (YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("--step", type=int, default=120, help="Time step in seconds")

    args = parser.parse_args()

    start_time = datetime.fromisoformat(args.start)
    end_time = datetime.fromisoformat(args.end)
    time_step = timedelta(seconds=args.step)

    inspect_tii_file(args.filename, start_time, end_time, time_step)
