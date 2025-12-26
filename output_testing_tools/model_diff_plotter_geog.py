import matplotlib.pyplot as plt
import numpy as np
from lompe.utils.save_load_utils import load_model
from lompe.model.visualization import format_ax, plot_potential
import os

def plot_grouped_components(file1, file2, outdir):
    model1 = load_model(file1, time='first')
    model2 = load_model(file2, time='first')

    # all lompe plot objects of interest (that have multiple components)
    grouped_components = {
        'Velocity': {
            'components': ['East', 'North'],
            'getter': lambda m: m.v(),
            'grid': 'J',
            'cmap': 'viridis',
            'diff_cmap': 'RdBu_r'
        },
        'E-field': {
            'components': ['East', 'North'],
            'getter': lambda m: m.E(),
            'grid': 'J',
            'cmap': 'plasma',
            'diff_cmap': 'RdBu_r'
        },
        'Current': {
            'components': ['East', 'North'],
            'getter': lambda m: m.j(),
            'grid': 'J',
            'cmap': 'autumn',
            'diff_cmap': 'RdBu_r'
        },
        'B_ground': {
            'components': ['East', 'North', 'Up'],
            'getter': lambda m: m.B_ground(),
            'grid': 'E',
            'cmap': 'jet',
            'diff_cmap': 'RdBu_r'
        },
        'Space FAC': {
            'components': ['East', 'North'],
            'getter': lambda m: m.B_space_FAC(),
            'grid': 'E',
            'cmap': 'gnuplot2',
            'diff_cmap': 'RdBu_r'
        },
        'Space Mag': {
            'components': ['East', 'North', 'Up'],
            'getter': lambda m: m.B_space(),
            'grid': 'E',
            'cmap': 'ocean',
            'diff_cmap': 'RdBu_r'
        },
        'FAC': {
            'components': [''],
            'getter': lambda m: m.FAC(),
            'grid': 'J',
            'cmap': 'coolwarm',
            'diff_cmap': 'RdBu_r'
        }
    }

    for group_name, comp in grouped_components.items():
        num_components = len(comp['components'])
        fig, axs = plt.subplots(num_components, 3, figsize=(20, 4 * num_components), squeeze=False)

        for i in range(num_components):
            try:
                d1 = comp['getter'](model1)
                d2 = comp['getter'](model2)
                if group_name != 'FAC':
                    d1 = d1[i]
                    d2 = d2[i]

                grid = getattr(model1, f'grid_{comp["grid"]}')
                shape = grid.shape
                xi = grid.xi_mesh
                eta = grid.eta_mesh

                d1 = d1.reshape(shape)
                d2 = d2.reshape(shape)
                diff = d2 - d1

                axs[i, 0].pcolormesh(xi, eta, d1, shading='auto', cmap=comp['cmap'])
                axs[i, 0].set_title(f"{group_name} {comp['components'][i]} - File 1")
                format_ax(axs[i, 0], model1)
                plt.colorbar(axs[i, 0].collections[0], ax=axs[i, 0], shrink=0.8)

                axs[i, 1].pcolormesh(xi, eta, d2, shading='auto', cmap=comp['cmap'])
                axs[i, 1].set_title(f"{group_name} {comp['components'][i]} - File 2")
                format_ax(axs[i, 1], model2)
                plt.colorbar(axs[i, 1].collections[0], ax=axs[i, 1], shrink=0.8)

                axs[i, 2].pcolormesh(xi, eta, diff, shading='auto', cmap=comp['diff_cmap'])
                axs[i, 2].set_title(f"{group_name} {comp['components'][i]} - Difference")
                format_ax(axs[i, 2], model1)
                plt.colorbar(axs[i, 2].collections[0], ax=axs[i, 2], shrink=0.8)

            except Exception as e:
                print(f" Error plotting {group_name} component {i}: {e}")
                axs[i, 0].axis('off')
                axs[i, 1].axis('off')
                axs[i, 2].axis('off')

        fig.tight_layout()
        outpath = os.path.join(outdir, f"{group_name.replace(' ', '_').lower()}_comparison.png")
        fig.savefig(outpath, dpi=1200, bbox_inches='tight', facecolor='white')
        plt.close(fig)

    # Separate plot for potential
    try:
        fig, axs = plt.subplots(1, 3, figsize=(18, 6))

        img1 = plot_potential(axs[0], model1)
        axs[0].set_title("Electric Potential (V) - File 1")
        format_ax(axs[0], model1)
        plt.colorbar(img1, ax=axs[0], shrink=0.8)

        img2 = plot_potential(axs[1], model2)
        axs[1].set_title("Electric Potential (V) - File 2")
        format_ax(axs[1], model2)
        plt.colorbar(img2, ax=axs[1], shrink=0.8)

        V1 = model1.E_pot().reshape(model1.grid_J.shape) * 1e-3
        V2 = model2.E_pot().reshape(model2.grid_J.shape) * 1e-3
        V1 = V1 - V1.min() - (V1.max() - V1.min()) / 2
        V2 = V2 - V2.min() - (V2.max() - V2.min()) / 2
        diff = np.abs(V2 - V1)

        img3 = axs[2].contourf(model1.grid_J.xi, model1.grid_J.eta, diff, cmap='RdBu_r')
        axs[2].set_title("Electric Potential (V) - Difference")
        format_ax(axs[2], model1)
        plt.colorbar(img3, ax=axs[2], shrink=0.8)

        fig.tight_layout()
        fig.savefig(os.path.join(outdir, "electric_potential_comparison.png"), dpi=600, bbox_inches='tight', facecolor='white')
        plt.close(fig)

    except Exception as e:
        print(f" Error plotting electric potential: {e}")

# USER INPUTS HERE
#file1 = '/Users/clevenger/Projects/paper01/events/20230227/lompe_weighting_test/pfisr_fov/lompe_outputs/20250613_outputs/0/2023-02-27_083500.nc'
#file2 = '/Users/clevenger/Projects/paper01/events/20230227/lompe_weighting_test/pfisr_fov/lompe_outputs/20250613_outputs/16_tii/everything_but_tii/2023-02-27_083500.nc'
#file1 = '/Users/clevenger/Projects/paper01/events/20230227/lompe/17_all_ground/2023-02-27_083500.nc'
#file2 = '/Users/clevenger/Projects/paper01/events/20230227/lompe/18_all_space/2023-02-27_083500.nc'
#outdir = '/Users/clevenger/Projects/paper01/events/20230227/lompe/diff_plots/35/'
#plot_grouped_components(file1, file2, outdir)

direc = '/Users/clevenger/Projects/paper01/events/20230227/lompe/individual_contribution_sensitivity_test/'
fn = '2023-02-27_083500.nc'
all = '13_all/'
file0 = direc + all + fn
outdir = '/Users/clevenger/Projects/paper01/events/20230227/lompe/iweight_sensitivity_test/diff_plots/'

"""
PFISR FOCUS
"""
all_pfisr = '08_pfisr/just_pfisr/'
none_pfisr = '08_pfisr/all_but_pfisr/'

# | All - PFISR |
file1 = direc + all_pfisr + fn
outdir0 = outdir + '0/'
plot_grouped_components(file0, file1, outdir0)

# | All - All but PFISR |
file2 = direc + none_pfisr + fn
outdir1 = outdir + '1/'
plot_grouped_components(file0, file2, outdir1)

# | All but PFISR - PFISR |
outdir2 = outdir + '2/'
plot_grouped_components(file2, file1, outdir2)


"""
SUPERDARN FOCUS
"""
all_kod = '07_kod/just_kod/'
none_kod = '07_kod/all_but_kod/'

# | All - KOD |
file3 = direc + all_kod + fn
outdir3 = outdir + '3/'
plot_grouped_components(file0, file3, outdir3)

# | All - All but KOD |
file4 = direc + none_kod + fn
outdir4 = outdir + '4/'
plot_grouped_components(file0, file4, outdir4)

# | All but KOD - KOD |
outdir5 = outdir + '5/'
plot_grouped_components(file4, file3, outdir5)


"""
SWARM A TII FOCUS
"""
all_tiia = '10_tiia/just_tiia/'
none_tiia = '10_tiia/all_but_tiia/'

# | All - TIIA |
file5 = direc + all_tiia + fn
outdir6 = outdir + '6/'
plot_grouped_components(file0, file5, outdir6)

# | All - All but TIIA |
file6 = direc + none_tiia + fn
outdir7 = outdir + '7/'
plot_grouped_components(file0, file6, outdir7)

# | All but KOD - KOD |
outdir8 = outdir + '8/'
plot_grouped_components(file6, file5, outdir8)


"""
CONVECTION FOCUS
"""
convecs = '01_all_convecs/'
no_convecs = '03_all_mags/'

# | All - Convecs |
file7 = direc + convecs + fn
outdir18 = outdir + '18/'
plot_grouped_components(file0, file7, outdir18)

# | All - All but Convecs |
file8 = direc + no_convecs + fn
outdir19 = outdir + '19/'
plot_grouped_components(file0, file8, outdir19)

# | All but Convecs - Convecs |
outdir20 = outdir + '20/'
plot_grouped_components(file8, file7, outdir20)

# |Convecs - PFISR|
outdir21 = outdir + '21/'
plot_grouped_components(file7, file1, outdir21)

# |Convecs - SD KOD|
outdir22 = outdir + '22/'
plot_grouped_components(file7, file3, outdir22)

# |Convecs - TIIA|
outdir23 = outdir + '23/'
plot_grouped_components(file7, file5, outdir23)


"""
SUPERMAG FOCUS
"""
all_gmag = '09_gmag/just_gmag/'
none_gmag = '09_gmag/all_but_gmag/'

# | All - SuperMag |
file9 = direc + all_gmag + fn
outdir9 = outdir + '9/'
plot_grouped_components(file0, file9, outdir9)

# | All - All but SuperMag |
file10 = direc + none_gmag + fn
outdir10 = outdir + '10/'
plot_grouped_components(file0, file10, outdir10)

# | All but SuperMag - SuperMag |
outdir11 = outdir + '11/'
plot_grouped_components(file10, file9, outdir11)


"""
SWARM MAG A FOCUS
"""
all_smaga = '11_smaga/just_smaga/'
none_smaga = '11_smaga/all_but_smaga/'

# | All - Swarm Mag A |
file11 = direc + all_smaga + fn
outdir12 = outdir + '12/'
plot_grouped_components(file0, file11, outdir12)

# | All - All but Swarm Mag A |
file12 = direc + none_smaga + fn
outdir13 = outdir + '13/'
plot_grouped_components(file0, file12, outdir13)

# | All but Swarm Mag A - Swarm Mag A |
outdir14 = outdir + '14/'
plot_grouped_components(file12, file11, outdir14)


"""
SWARM MAG C FOCUS
"""
all_smagc = '12_smagc/just_smagc/'
none_smagc = '12_smagc/all_but_smagc/'

# | All - Swarm Mag C |
file13 = direc + all_smagc + fn
outdir15 = outdir + '15/'
plot_grouped_components(file0, file13, outdir15)

# | All - All but Swarm Mag C |
file14 = direc + none_smagc + fn
outdir16 = outdir + '16/'
plot_grouped_components(file0, file14, outdir16)

# | All but Swarm Mag C - Swarm Mag C |
outdir17 = outdir + '17/'
plot_grouped_components(file14, file13, outdir17)


"""
MAG FOCUS
"""
all_mags = '03_all_mags/'
no_mags = '01_all_convecs/'
space_mags = '04_just_space_mags/'

# | All - Mags |
file15 = direc + all_mags + fn
outdir24 = outdir + '24/'
plot_grouped_components(file0, file15, outdir24)

# | All - All but Mags |
file16 = direc + no_mags + fn
outdir25 = outdir + '25/'
plot_grouped_components(file0, file16, outdir25)

# | All but Mags - Mags |
outdir26 = outdir + '26/'
plot_grouped_components(file16, file15, outdir26)

# | Mags - SuperMag |
outdir27 = outdir + '27/'
plot_grouped_components(file15, file9, outdir27)

# | Mags - Swarm A Mag |
outdir28 = outdir + '28/'
plot_grouped_components(file15, file11, outdir28)

# | Mags - Swarm C Mag |
outdir29 = outdir + '29/'
plot_grouped_components(file15, file13, outdir29)

# | Swarm A Mag - Swarm C Mag |
outdir30 = outdir + '30/'
plot_grouped_components(file11, file13, outdir30)

# | Space Mags - Swarm A Mag |
file17 = direc + space_mags + fn
outdir31 = outdir + '31/'
plot_grouped_components(file17, file11, outdir31)

# | Space Mags - Swarm C Mag |
outdir32 = outdir + '32/'
plot_grouped_components(file17, file13, outdir32)


"""
SPACE & GROUND FOCUS
"""
ground = '05_all_ground/'
space = '06_all_space/'

# | All - Ground |
file18 = direc + ground + fn
outdir33 = outdir + '33/'
plot_grouped_components(file0, file18, outdir33)

# | All - Space |
file19 = direc + space + fn
outdir34 = outdir + '34/'
plot_grouped_components(file0, file19, outdir34)

# | Ground - Space |
outdir35 = outdir + '35/'
plot_grouped_components(file18, file19, outdir35)
