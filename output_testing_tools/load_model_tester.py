from lompe.utils.save_load_utils import load_model


file='/your_file_path_to_model_outputs/2023-02-12_064500.nc'
loaded_model = load_model(file, time='first')

ve, vn = loaded_model.v(-147, 65) # lon, lat
print("ve: ", ve) 
print("vn: ", vn)

fac = loaded_model.FAC(-147, 65)
print("FAC: ", fac)

fac_all = loaded_model.FAC()
print("FAC shape: ", fac_all.shape)

efield = loaded_model.E(-147, 65)
print("E-Field: ", efield)