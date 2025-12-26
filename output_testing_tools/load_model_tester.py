from lompe.utils.save_load_utils import load_model

file = '/Users/clevenger/Projects/paper01/events/20230227/lompe_weighting_test/4/2023-02-27_083500.nc'
loaded_model = load_model(file, time='first')

# Velocity components
ve, vn = loaded_model.v()  # Returns arrays
print("ve shape:", ve.shape)
print("vn shape:", vn.shape)

# Field-aligned current (array)
fac = loaded_model.FAC()
print("FAC shape:", fac.shape)

# E-field components (tuple of arrays)
efield = loaded_model.E()
print("E-Field components:")
for i, component in enumerate(efield):
    print(f"  Component {i+1} shape:", component.shape)

# Ground magnetic field (tuple of arrays)
b_ground = loaded_model.B_ground()
print("B-Field (ground) components:")
for i, component in enumerate(b_ground):
    print(f"  Component {i+1} shape:", component.shape)

# Current components (tuple of arrays)
e_curr = loaded_model.j()
print("Electric Current components:")
for i, component in enumerate(e_curr):
    print(f"  Component {i+1} shape:", component.shape)

# Space FAC (array)
space_fac = loaded_model.B_space_FAC()
print("Space FAC components:")
for i, component in enumerate(space_fac):
    print(f"  Component {i+1} shape:", component.shape)

# Space magnetic field (array)
space_mag = loaded_model.B_space()
print("Space Mag components:")
for i, component in enumerate(space_mag):
    print(f"  Component {i+1} shape:", component.shape)
