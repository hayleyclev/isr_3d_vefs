#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 11:54:10 2023

@author: clevenger
"""

import pandas as pd

# Provide file path to desired csv for conversion
csv_file_path = '/Users/clevenger/Projects/lompe_pfisr/mag_data/poker_mag/06162017/csv_inputs/poker_2017_06_16.csv/poker_2017_06_16.csv'

# Provide file path for where you want h5 to be saved
hdf5_file_path = '/Users/clevenger/Projects/lompe_pfisr/mag_data/poker_mag/06162017/h5_outputs/poker_2017_06_16.h5'


# Read the CSV file into a pandas DataFrame
df = pd.read_csv(csv_file_path)

# Write the DataFrame to an HDF5 file
df.to_hdf(hdf5_file_path, key='data', mode='w')
