#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 17:37:41 2024

@author: clevenger
"""

import numpy as np
import pandas as pd
import datetime as dt
from viresclient import SwarmRequest
import viresclient
import lompe

# Function to collect data from the Swarm satellite
def get_swarm_data(start_time, end_time, prime):
    # Set the request parameters for Swarm EFI data
    request = SwarmRequest()
    request.set_collection(prime)
    request.set_products(measurements=['VixE', 'VixN', 'Viy', 'Viz'],  # Ion drifts in NEC frame
                         auxiliaries=['QDLat', 'QDLon', 'MLT'],  # Magnetic coordinates
                         sampling_step='PT1S')  # 1-second sampling rate
    
    # Fetch the data between start_time and end_time
    data = request.get_between(start_time, end_time)
    df = data.as_dataframe()
    
    # Calculate vlos, coords, and los for lompe.Data object
    vlos = df[['VixE', 'VixN', 'Viy', 'Viz']].to_numpy()
    coords = df[['QDLat', 'QDLon']].to_numpy().T  # Magnetic coordinates as location
    los = np.ones_like(vlos)  # Placeholder; LOS vector needs to be calculated based on the context
    
    return vlos, coords, los

# Function to create lompe.Data object for the Swarm data
def create_lompe_data(vlos, coords, los):
    # Create lompe.Data object with the Swarm data
    swarm_flow_data = lompe.Data(vlos, coordinates=coords, LOS=los, datatype='convection', scale=None)
    return swarm_flow_data

# Main script to set parameters and fetch data
if __name__ == '__main__':
    # Set your token securely
    viresclient.set_token('YOUR_TOKEN_HERE')

    # Specify the start and end times
    start_time = dt.datetime(2023, 3, 19, 18, 25)
    end_time = dt.datetime(2023, 3, 19, 18, 30)
    
    # Specify the collection for EFI data
    prime = "SW_EXPT_EFIA_TCT02"

    # Fetch the Swarm data
    vlos, coords, los = get_swarm_data(start_time, end_time, prime)

    # Check if any data was returned
    if not vlos.size:
        print("No data was fetched for the given time range.")
    else:
        # Create lompe.Data object
        swarm_flow_data = create_lompe_data(vlos, coords, los)

        # Here you would add the data to a lompe model and run inversion
        # This is pseudocode and would need to be replaced with your actual model usage
        # model.add_data(swarm_flow_data)
        # model.run_inversion(l1=1, l2=0.1)
        # ...

        # Example of saving or plotting the results
        # savepath = '/path/to/your/save/location'
        # model.plot_results(savepath)



