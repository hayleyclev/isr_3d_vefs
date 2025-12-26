import os


def read_asi(start_time, end_time, asi_filepath):

    imgs = []  # list to hold all images - converted to xarray later
    
    for asi_fn in asi_filepath:
        files = glob.glob(asi_filepath + '*' + /d_yyyymmdd + '*.NC')

        files.sort()
        if len(files) == 0:
            continue

        ii = 0  # counter
        ii_max = len(files)


        if len(extra_file) == 1:
            files.append(extra_file[0])

        for file in files:
            f = netCDF4.Dataset(file)

            mlat = f.variables['Magnetic Latitude'][:]
            mlon = f.variables['Magnetic Longitude'][:]
            mlt = filename d_/
            uthr = filename d_/
            doy = filename d_/
            year = filename d_/

            #wavelengths = f.variables['DISK_RADIANCEDATA_INTENSITY_' + hemi.upper()][:]
            char_energy = f.variables['E0'][:]
            energyflux = f.variables['Q'][:]

            f.close()

            mask = uthr == 0

            uthr[mask] = np.nan
            #wavelengths[:, mask] = np.nan
            char_energy[mask] = np.nan
            energyflux[mask] = np.nan
            mlon[mask] = np.nan

            # applying Robinson formulas to calculate conductances: https://agupubs.onlinelibrary.wiley.com/doi/epdf/10.1029/JA092iA03p02565
            SP = (40. * char_energy * np.sqrt(energyflux)) / \
                (16. + char_energy**2)
            SH = 0.45 * char_energy**0.85 * SP

            if sum(np.isfinite(uthr[:, 181]).flatten()) > 0:  # there is data in north
                # Calculate center time:
                # there is a sudden transition across midnight in the pass
                if np.nanstd(uthr) > 0.5:
                    next_day = (uthr > 0) & (uthr < 2)
                    if sum(next_day.flatten()) > 0:
                        uthr[next_day] = uthr[next_day] + 24.
                center_hr = np.nanmean(uthr, axis=0)[181]
                if (ii == 0) & (center_hr >= 22):
                    ii = + 1
                    # the image is (likely) from the previous day
                    continue

                if (ii == ii_max) & (center_hr < 22):
                    ii = + 1
                    continue              # the image is not from the same day and is skipped

                if (ii == ii_max):
                    doy = doy - 1

                hr = int(center_hr)
                if hr >= 24:
                    hr = hr - 24
                    center_hr = center_hr - 24

                m = int((center_hr - hr)*60)
                s = round(((center_hr - hr)*60 - m)*60)
                if s == 60:
                    t0 = dt.datetime(year, 1, 1, hr, m, 59) + \
                        dt.timedelta(seconds=1)
                else:
                    t0 = dt.datetime(year, 1, 1, hr, m, s)

                dtime = t0 + dt.timedelta(doy - 1)
                # put into xarray object
                img = xr.Dataset({'uthr': (['row', 'col'], uthr),
                                  'mlon': (['row', 'col'], mlon),
                                  'mlat': (['row', 'col'], mlat),
                                  'E0': (['row', 'col'], char_energy),
                                  'je': (['row', 'col'], energyflux),
                                  'SP': (['row', 'col'], SP),
                                  'SH': (['row', 'col'], SH)})
                img = img.expand_dims(date=[dtime])
                img = img.assign({'satellite': sat})
                img = img.assign(
                    {'orbit': file.split('_SN.')[-1].split('-')[0]})
                imgs.append(img)
            ii += 1

    if len(imgs) == 0:
        print('No SSUSI images found.')
        return None

    else:     # save as netcdf in specified path
        imgs = xr.concat(imgs, dim='date')
        imgs = imgs.sortby(imgs['date'])
        print('DMSP SSUSI file saved: ' + savefile)

        imgs.to_netcdf(savefile)

        return savefile
