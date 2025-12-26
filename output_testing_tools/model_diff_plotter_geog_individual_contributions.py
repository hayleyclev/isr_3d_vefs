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

direc = '/Users/clevenger/Projects/paper01/events/20230227/lompe/iweight_sensitivity_test/'
fn = '2023-02-27_083500.nc'
outdir = '/Users/clevenger/Projects/paper01/events/20230227/lompe/iweight_sensitivity_test/diff_plots/'

file0 = direc + '0/' + fn # everything weighted the same
file1 = direc + '1/' + fn # hypothesized "perfect" test case
file2 = direc + '2/' + fn  # "perfect", heightening sd
file3 = direc + '3/' + fn  # "perfect", lowering swarm
file4 = direc + '4/' + fn  # "perfect", heightening sd & lowering swarm
file5 = direc + '5/' + fn  # "perfect", raising supermag
file6 = direc + '6/' + fn  # "perfect", raising supermag & sd
file7 = direc + '7/' + fn  # "perfect", raising supermag & sd, lowering swarm
file8 = direc + '8/' + fn  # "perfect", lowering swarm mag only
file9 = direc + '9/' + fn  # "perfect", lowering sd
file10 = direc + '10/' + fn  # "perfect", raising swarm
file11 = direc + '11/' + fn  # everything at half other than pfisr
file12 = direc + '12/' + fn  # everything at half or third other than pfisr (crosstracks at half)
file13 = direc + '13/' + fn  # everything at half or third other than pfisr (crosstracks at third)
file14 = direc + '14/' + fn  # everything at half or third other than pfisr (edges at half)
file15 = direc + '15/' + fn  # everything at half or third other than pfisr (edges at third)

"""
| EVERYTHING WEIGHTED THE SAME - EACH CASE |
"""
# | 0 - 1 |
outdir0 = outdir + '0/'
plot_grouped_components(file0, file1, outdir0)

# | 0 - 2 |
outdir1 = outdir + '1/'
plot_grouped_components(file0, file2, outdir1)

# | 0 - 3 |
outdir2 = outdir + '2/'
plot_grouped_components(file0, file3, outdir2)

# | 0 - 4 |
outdir3 = outdir + '3/'
plot_grouped_components(file0, file4, outdir3)

# | 0 - 5 |
outdir4 = outdir + '4/'
plot_grouped_components(file0, file5, outdir4)

# | 0 - 6 |
outdir5 = outdir + '5/'
plot_grouped_components(file0, file6, outdir5)

# | 0 - 7 |
outdir6 = outdir + '6/'
plot_grouped_components(file0, file7, outdir6)

# | 0 - 8 |
outdir7 = outdir + '7/'
plot_grouped_components(file0, file8, outdir7)

# | 0 - 9 |
outdir8 = outdir + '8/'
plot_grouped_components(file0, file9, outdir8)

# | 0 - 10 |
outdir9 = outdir + '9/'
plot_grouped_components(file0, file10, outdir9)

# | 0 - 11 |
outdir10 = outdir + '10/'
plot_grouped_components(file0, file11, outdir10)

# | 0 - 12 |
outdir11 = outdir + '11/'
plot_grouped_components(file0, file12, outdir11)

# | 0 - 13 |
outdir12 = outdir + '12/'
plot_grouped_components(file0, file13, outdir12)

# | 0 - 14 |
outdir13 = outdir + '13/'
plot_grouped_components(file0, file14, outdir13)

# | 0 - 15 |
outdir14 = outdir + '14/'
plot_grouped_components(file0, file15, outdir14)
