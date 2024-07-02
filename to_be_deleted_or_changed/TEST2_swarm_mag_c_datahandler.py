#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 21:24:44 2024

@author: clevenger
"""

import lompe
import numpy as np
from viresclient import SwarmRequest
import viresclient
from secsy import cubedsphere as cs
import datetime as dt
import pandas as pd
import apexpy
import ppigrf
import dipole
import matplotlib.pyplot as plt

def collect_data(start_time, end_time):
    viresclient.set_token()
    prime = "SW_OPER_MAGC_LR_1B"
    DT = dt.timedelta(seconds=5 * 60)

    current_time = start_time
    all_data = []

    while current_time <= end_time:
        t0 = current_time
        a = apexpy.Apex(t0)

        request = SwarmRequest()
        request.set_collection(prime)
        request.set_products(
            measurements=["B_NEC"],
            models=["CHAOS"],
        )

        data = request.get_between(t0 - DT, t0 + DT)
        df = data.as_dataframe()

        if df.empty:
            print(f"No data for time interval {t0 - DT} to {t0 + DT}")
            current_time += dt.timedelta(minutes(1)
            continue

        dB = np.vstack(df.B_NEC.values - df.B_NEC_CHAOS.values)
        gdlat, height, Bn, Bu = ppigrf.ppigrf.geoc2geod(
            90 - df.Latitude.values, df.Radius.values * 1e-3, -dB[:, 0], -dB[:, 2]
        )

        df['Bn'], df['Be'], df['Bu'] = Bn, dB.T[1, 0], Bu

        lat_range = (45, 75)
        lon_range = (-175, -130)
        outside_range = ~df['Latitude'].between(*lat_range) | ~df['Longitude'].between(*lon_range)
        df.loc[outside_range, ['Bn', 'Be', 'Bu']] = np.nan

        lo = df.Longitude.values * np.pi / 180
        la = df.Latitude.values * np.pi / 180
        r = np.vstack((np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)))
        r = r * df.Radius.values.reshape((1, -1))

        dr = r[:, 1:] - r[:, :-1]
        v_enu = dipole.ecef_to_enu(dr.T, df.Longitude[:-1].values, df.Latitude[:-1].values).T
        v_enu = v_enu[:, v_enu.shape[1] // 2]
        v_enu = v_enu / np.linalg.norm(v_enu)

        p = cs.CSprojection((np.rad2deg(lo[lo.size // 2]), np.rad2deg(la[lo.size // 2])), orientation=v_enu[:2])
        grid = cs.CSgrid(p, 2000.e3, 1000.e3, 40.e3, 50.e3, R=(6371.2 + 110) * 1e3)

        model = lompe.Emodel(grid, (lambda lon, lat: conductance(lon, lat, 'h'), lambda lon, lat: conductance(lon, lat, 'p')))

        dB = np.vstack((df.Be.values, df.Bn.values, df.Bu.values))
        coords = np.vstack((df.Longitude.values, df.Latitude.values, (6371.2 + height) * 1e3))
        swarm_mag_c_data = lompe.Data(values=dB * 1e-9, coordinates=coords, datatype='space_mag_full', iweight=0.4)

        all_data.append(swarm_mag_c_data)
        current_time += dt.timedelta(minutes=1)

    return all_data
