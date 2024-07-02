from lompe_fitacf_reading import fitacf_get_lompe_params
import glob
import datetime as dt


def read_superdarn_data(superdarn_direc, start_time, DT):
    fitacf_dir = superdarn_direc
    fitacf_files = {
        'kod': glob.glob(f"{fitacf_dir}/kod/*.fitacf"),
        'ksr': glob.glob(f"{fitacf_dir}/ksr/*.fitacf")#,
        #'ade': glob.glob(f"{fitacf_dir}/ade/*.fitacf"),
        #'adw': glob.glob(f"{fitacf_dir}/adw/*.fitacf")
        }

    time_of_interest = dt.datetime.strptime(start_time)
    #start_time = dt.datetime.strptime('2017-06-06 23:00:00', '%Y-%m-%d %H:%M:%S')
    #end_time = dt.datetime.strptime('2017-06-06 23:00:00', '%Y-%m-%d %H:%M:%S')
    DT = DT


    radar_data_chunked = fitacf_get_lompe_params(fitacf_dir, fitacf_files, time_of_interest, DT)
    #radar_data = fitacf_get_lompe_params(fitacf_dir, fitacf_files, start_time, end_time, DT)


    # Print the data
    for radar_id, data in radar_data_chunked.items():
        print(f"{radar_id} vlos:", data['vlos'])
        print(f"{radar_id} vlos:", data['vlos'].shape)
        print(f"{radar_id} vlos_err:", data['vlos_err'])
        print(f"{radar_id} vlos_err:", data['vlos_err'].shape)
        print(f"{radar_id} coords:", data['coords'])
        print(f"{radar_id} coords:", data['coords'].shape)
        print(f"{radar_id} los:", data['los'])
        print(f"{radar_id} los:", data['los'].shape)
        print()  # Just for a new line for readability
    
    return radar_data_chunked

