from lompe_fitacf_reading import fitacf_get_lompe_params
import glob
import datetime as dt

fitacf_dir = '/Users/clevenger/Projects/lompe_pfisr/superdarn_data/06062017'
fitacf_files = {
    'kod': glob.glob(f"{fitacf_dir}/kod/*.fitacf"),
    'ksr': glob.glob(f"{fitacf_dir}/ksr/*.fitacf"),
    'ade': glob.glob(f"{fitacf_dir}/ade/*.fitacf"),
    'adw': glob.glob(f"{fitacf_dir}/adw/*.fitacf")
    }

time_of_interest = dt.datetime.strptime('2017-06-06 23:00:00', '%Y-%m-%d %H:%M:%S')
#start_time = dt.datetime.strptime('2017-06-06 23:00:00', '%Y-%m-%d %H:%M:%S')
#end_time = dt.datetime.strptime('2017-06-06 23:00:00', '%Y-%m-%d %H:%M:%S')
DT = dt.timedelta(seconds = 5 * 60)


radar_data = fitacf_get_lompe_params(fitacf_dir, fitacf_files, time_of_interest, DT)
#radar_data = fitacf_get_lompe_params(fitacf_dir, fitacf_files, start_time, end_time, DT)


# Print the data
for radar_id, data in radar_data.items():
    print(f"{radar_id} vlos:", data['vlos'])
    print(f"{radar_id} vlos_err:", data['vlos_err'])
    print(f"{radar_id} coords:", data['coords'])
    print(f"{radar_id} los:", data['los'])
    print()  # Just for a new line for readability

