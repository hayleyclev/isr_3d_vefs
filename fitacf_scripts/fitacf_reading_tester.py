import pydarn

file_path_to_fitacf_tester = '/Users/clevenger/Projects/lompe_pfisr/superdarn_data/06062017/ksr/20170606.0001.00.ksr.a.fitacf'

reader = pydarn.SuperDARNRead(file_path_to_fitacf_tester)
data = reader.read_fitacf()

for record in data:
    if 'slist' in record:
        print(record['slist'])
    else:
        print('No slist found in this record')
