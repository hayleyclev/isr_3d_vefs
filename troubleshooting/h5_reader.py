import h5py

def inspect_h5(filepath):
    def print_attrs(name, obj):
        if isinstance(obj, h5py.Dataset):
            print(f"[Dataset] {name}")
            print(f"   shape: {obj.shape}")
            print(f"   dtype: {obj.dtype}")
        elif isinstance(obj, h5py.Group):
            print(f"[Group]   {name}")

    with h5py.File(filepath, 'r') as f:
        print(f"Inspecting: {filepath}\n")
        f.visititems(print_attrs)

inspect_h5("/Users/clevenger/Projects/paper01/events/20230208/raw_data/20230208.001_lp_5min-fitcal.h5")
