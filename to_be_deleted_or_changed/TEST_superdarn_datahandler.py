#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 23:15:00 2024

@author: clevenger
"""

import math
import pydarn
import datetime as dt
import numpy as np
from lompe.data_tools.dataloader import los_azimuth2en
from pydarn.utils.coordinates import gate2geographic_location
import glob
import lompe


def collect_data(fitacf_dir, time_intervals, radar_id):
    fitacf_files = glob.glob(f"{fitacf_dir}/{radar_id}/*")
    glon_list, glat_list, vlos_list, vlos_err_list, le_list, ln_list = [], [], [], [], [], []

    for fitacf_file in fitacf_files:
        sdarn_read = pydarn.SuperDARNRead(fitacf_file)
        fitacf_data = sdarn_read.read_fitacf()
        stid = fitacf_data[0]['stid']
        record_times = [dt.datetime(fitacf_data[x]['time.yr'], fitacf_data[x]['time.mo'], fitacf_data[x]['time.dy'],
                                    fitacf_data[x]['time.hr'], fitacf_data[x]['time.mt'], fitacf_data[x]['time.sc'],
                                    fitacf_data[x]['time.us']) for x in range(len(fitacf_data))]
        unix_record_times = np.array([(t0-dt.datetime.utcfromtimestamp(0)).total_seconds() for t0 in record_times])

        for n, (t0, t1) in enumerate(time_intervals):
            t0_unix = (t0-dt.datetime.utcfromtimestamp(0)).total_seconds()
            t1_unix = (t1-dt.datetime.utcfromtimestamp(0)).total_seconds()
            chunk_indices = np.argwhere((t0_unix <= unix_record_times) & (unix_record_times <= t1_unix))
            chunk_indices = np.squeeze(chunk_indices)

            glon, glat, vlos, vlos_err, le, ln = [], [], [], [], [], []

            for i in chunk_indices:
                slist = fitacf_data[i]['slist']
                gflg = fitacf_data[i]['gflg']
                try:
                    rsep = fitacf_data[i]['rsep']
                except KeyError:
                    rsep = 45
                try:
                    frang = fitacf_data[i]['frang']
                except KeyError:
                    frang = 180

                beam = fitacf_data[i]['bmnum']

                for j, gate in enumerate(slist):
                    if gflg[j] == 0 and abs(fitacf_data[i]['v'][j]) <= 2000 and gate > 10:
                        lat, lon = gate2geographic_location(stid=stid, beam=beam, range_gate=gate, height=300,
                                                            center=True, rsep=rsep, frang=frang)
                        azm = fitacf_get_k_vector(stid, lat, lon, fitacf_data[i]['v'][j])
                        le_current, ln_current = los_azimuth2en(azm)

                        glat.append(lat)
                        glon.append(lon)
                        vlos.append(abs(fitacf_data[i]['v'][j]))
                        vlos_err.append(abs(fitacf_data[i]['v_e'][j]))
                        le.append(le_current)
                        ln.append(ln_current)
                        
            # Find the maximum length of the arrays
            max_length = max(len(glon), len(glat), len(vlos), len(vlos_err), len(le), len(ln))

            #glon_list.append(glon)
            #glat_list.append(glat)
            #vlos_list.append(np.pad(vlos, (0, max_length - len(vlos)), 'constant', constant_values=np.nan))
            #vlos_err_list.append(np.pad(vlos_err, (0, max_length - len(vlos_err)), 'constant', constant_values=np.nan))
            #le_list.append(np.pad(le, (0, max_length - len(le)), 'constant', constant_values=np.nan))
            #ln_list.append(np.pad(ln, (0, max_length - len(ln)), 'constant', constant_values=np.nan))
            
            # Now pad each array to match the max_length
            glon_list.append(np.pad(glon, (0, max_length - len(glon)), 'constant', constant_values=np.nan))
            glat_list.append(np.pad(glat, (0, max_length - len(glat)), 'constant', constant_values=np.nan))
            vlos_list.append(np.pad(vlos, (0, max_length - len(vlos)), 'constant', constant_values=np.nan))
            vlos_err_list.append(np.pad(vlos_err, (0, max_length - len(vlos_err)), 'constant', constant_values=np.nan))
            le_list.append(np.pad(le, (0, max_length - len(le)), 'constant', constant_values=np.nan))
            ln_list.append(np.pad(ln, (0, max_length - len(ln)), 'constant', constant_values=np.nan))

        print('Done file: ' + fitacf_file)

    superdarn_data = []

    for i in range(len(glon_list)):
        superdarn_data.append(lompe.Data(vlos_list[i],
                                         coordinates=np.vstack((glon_list[i], glat_list[i])),
                                         LOS=np.vstack((le_list[i], ln_list[i])),
                                         datatype='convection', scale=None, iweight=1.0))

    return superdarn_data



def fitacf_get_k_vector(stid, lat, lon, v_los):
    radlat = pydarn.SuperDARNRadars.radars[stid].hardware_info.geographic.lat
    radlon = pydarn.SuperDARNRadars.radars[stid].hardware_info.geographic.lon

    vec_start_x = (90 - lat) * np.cos(np.radians(lon))
    vec_start_y = (90 - lat) * np.sin(np.radians(lon))
    radlat_x = (90 - radlat) * np.cos(np.radians(radlon))
    radlat_y = (90 - radlat) * np.sin(np.radians(radlon))

    theta = math.atan2(radlat_x - vec_start_x, radlat_y - vec_start_y)

    if v_los >= 1:
        vsign = 5
    else:
        vsign = -5
    vec = [(vsign * np.sin(theta)), (vsign * np.cos(theta))]

    origin_vec = [-vec_start_x, -vec_start_y]

    atana = math.atan2(vec[0],vec[1])
    atanb = math.atan2(origin_vec[0], origin_vec[1])
    kvect = np.degrees(atana - atanb)

    return kvect
