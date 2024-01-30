from fitacf_function_script_multi_time import fitacf_get_lompe_params
import glob
import datetime as dt
import h5py
import os

fitacf_dir = '/Users/clevenger/Projects/lompe_pfisr/test_datasets/superdarn/02122023'
fitacf_files = {
    'kod': glob.glob(f"{fitacf_dir}/kod/*.fitacf"),
    'ksr': glob.glob(f"{fitacf_dir}/ksr/*.fitacf")#,
    #'ade': glob.glob(f"{fitacf_dir}/ade/*.fitacf"),
    #'adw': glob.glob(f"{fitacf_dir}/adw/*.fitacf")
    }

#time_of_interest = dt.datetime.strptime('2023-02-12 20:00:00', '%Y-%m-%d %H:%M:%S')
start_time = dt.datetime.strptime('2023-02-12 14:00:00', '%Y-%m-%d %H:%M:%S')
end_time = dt.datetime.strptime('2023-02-12 19:00:00', '%Y-%m-%d %H:%M:%S')
DT = dt.timedelta(seconds = 5 * 60)


#radar_data = fitacf_get_lompe_params(fitacf_dir, fitacf_files, time_of_interest, DT)
radar_data = fitacf_get_lompe_params(fitacf_dir, fitacf_files, start_time, end_time, DT)

# Create hdf5 files
hdf5_files = {}
for radar_id in radar_data.keys():
    hdf5_filename = os.path.join(fitacf_dir, f"{radar_id}_data_{start_time}_{end_time}.h5")
    hdf5_files[radar_id] = h5py.File(hdf5_filename, 'w')
    
# Append data within hdf55 files for all of the time increments
for radar_id, data in radar_data.items():
    hdf5_file = hdf5_files[radar_id]
    hdf5_file.create_dataset('vlos', data=data['vlos'])
    hdf5_file.create_dataset('vlos_err', data=data['vlos_err'])
    hdf5_file.create_dataset('coords', data=data['coords'])
    hdf5_file.create_dataset('los', data=data['los'])
    hdf5_file.close()
    

# Print the data
for radar_id, data in radar_data.items():
    print(f"{radar_id} vlos:", data['vlos'])
    print(f"{radar_id} vlos:", data['vlos'].shape)
    print(f"{radar_id} vlos_err:", data['vlos_err'])
    print(f"{radar_id} vlos_err:", data['vlos_err'].shape)
    print(f"{radar_id} coords:", data['coords'])
    print(f"{radar_id} coords:", data['coords'].shape)
    print(f"{radar_id} los:", data['los'])
    print(f"{radar_id} los:", data['los'].shape)
    print()  # Just for a new line for readability