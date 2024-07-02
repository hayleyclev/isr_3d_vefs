#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 15:02:24 2024

@author: clevenger
"""

from lompe_fitacf_reading import fitacf_get_lompe_params
from superdarn_lompe_runscript import radar_data_chunked
from lompe_fitacf_reading import radar_data


def collect_data(superdarn_direc, time_intervals):
    
    # Read in superdarn kodiak (kod) data
    superdarn_kod_data = radar_data_chunked['kod']

    for i, (t0, t1) in enumerate(time_intervals):
        
        for radar_id, data in radar_data_chunked.items():
            print(f"{radar_id} vlos:", data['vlos'][i])
            print(f"{radar_id} vlos:", data['vlos'].shape)
            print(f"{radar_id} vlos_err:", data['vlos_err'])
            print(f"{radar_id} vlos_err:", data['vlos_err'].shape)
            print(f"{radar_id} coords:", data['coords'])
            print(f"{radar_id} coords:", data['coords'].shape)
            print(f"{radar_id} los:", data['los'])
            print(f"{radar_id} los:", data['los'].shape)
            print()  # Just for a new line for readability
        # Create Lompe data object for the magnetometer data
        superdarn_kod_data = lompe.Data(vlos, coordinates = coords, LOS = los, datatype = 'convection', scale = None)


    # Return the prepared data
    return superdarn_kod_data

def collect_data(superdarn_direc, time_intervals):
    
    return superdarn_ksr_data