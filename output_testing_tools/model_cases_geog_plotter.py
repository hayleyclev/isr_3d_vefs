import os
import numpy as np
import matplotlib.pyplot as plt
from lompe.utils.save_load_utils import load_model
from lompe.model.visualization import format_ax

# grab groups from lompe
def get_components(model, group_name):
    """Return (East, North) arrays for the requested physical group."""
    if group_name == "E-field":
        return model.E()
    elif group_name == "Space FAC":
        return model.B_space_FAC()
    else:
        raise ValueError(f"Unknown group: {group_name}")


def get_grid(model, group_name):
    """Return the proper grid for the given group."""
    grid_map = {
        "E-field": "J",
        "Space FAC": "E",
    }
    grid_key = grid_map.get(group_name)
    grid = getattr(model, f"grid_{grid_key}")
    return grid.shape, grid.xi_mesh, grid.eta_mesh


# plot groups
def plot_cases_matrix(parent_dir, filename, outdir,
                      baseline_case=0, ideal_case=17,
                      cases=None):

    if cases is None:
        cases = list(range(1, 17))
    # Ensure baseline and ideal are excluded
    cases = [c for c in cases if c not in (baseline_case, ideal_case)]

    groups = {
        "E-field": {"cmap": "viridis"},
        "Space FAC": {"cmap": "plasma"},
    }

    print("Loading baseline model...")
    base_model = load_model(os.path.join(parent_dir, str(baseline_case), filename), time="first")
    print("Loading ideal model...")
    ideal_model = load_model(os.path.join(parent_dir, str(ideal_case), filename), time="first")

    # compute grids for each group
    grid_cache = {}
    for group_name in groups.keys():
        print(f"Fetching grid for {group_name}...")
        shape, xi, eta = get_grid(base_model, group_name)
        print(f"  Grid shape: {shape}")
        grid_cache[group_name] = {"shape": shape, "xi": xi, "eta": eta}

    # compute baseline and ideal reshaped arrays
    data_cache = {}
    for group_name in groups.keys():
        shape = grid_cache[group_name]["shape"]
        print(f"Reshaping baseline and ideal for {group_name}...")
        data_cache[group_name] = {}
        data_cache[group_name]["baseline"] = [comp.reshape(shape) for comp in get_components(base_model, group_name)]
        data_cache[group_name]["ideal"] = [comp.reshape(shape) for comp in get_components(ideal_model, group_name)]

    # determine total rows/columns for figure
    total_rows = 2 + 2 * len(cases)
    total_cols = 6  # fixed

    print(f"Creating figure with {total_rows} rows x {total_cols} columns...")
    fig, axs = plt.subplots(
        total_rows, total_cols,
        figsize=(total_cols * 3.8, total_rows * 2.0),
        squeeze=False
    )

    row = 0

    # first block is different (shows baseline/ideal and diff)
    print("Plotting baseline and ideal blocks...")
    for comp_idx, comp_name in enumerate(["North–South", "East–West"]):
        for group_name in groups.keys():
            shape = grid_cache[group_name]["shape"]
            xi = grid_cache[group_name]["xi"]
            eta = grid_cache[group_name]["eta"]

            base_data = data_cache[group_name]["baseline"][comp_idx]
            ideal_data = data_cache[group_name]["ideal"][comp_idx]
            diff_data = np.abs(base_data - ideal_data)

            # set columns
            cols = [0, 1, 2] if group_name == "E-field" else [3, 4, 5]

            for col_idx, col in enumerate(cols):
                print(f"  Row {row}, plotting {group_name} ({comp_name}), column {col_idx}...")
                data_list = [base_data, ideal_data, diff_data]
                titles = ["Baseline", "Ideal", "|Baseline − Ideal|"]
                ax = axs[row, col]

                # Colormap: first two columns are baseline/ideal in original cmap, diff column uses 'bwr'
                if col_idx < 2:  # Baseline and Ideal
                    cmap_to_use = groups[group_name]["cmap"]
                else:  # Diff column
                    cmap_to_use = "bwr"

                m = ax.pcolormesh(xi, eta, data_list[col_idx], shading="auto", cmap=cmap_to_use)
                ax.set_title(f"{group_name} ({comp_name})\n{titles[col_idx]}", fontsize=9)
                format_ax(ax, base_model)
                fig.colorbar(m, ax=ax, shrink=0.75)
        row += 1

    # make the rest of the rows
    print("Plotting case rows...")
    for ci in cases:
        print(f"Loading case {ci}...")
        case_model = load_model(os.path.join(parent_dir, str(ci), filename), time="first")

        for comp_idx, comp_name in enumerate(["North–South", "East–West"]):
            for group_name in groups.keys():
                shape = grid_cache[group_name]["shape"]
                xi = grid_cache[group_name]["xi"]
                eta = grid_cache[group_name]["eta"]

                print(f"  Case {ci}, component {comp_name}, group {group_name}...")
                # Case data reshaped
                case_data = [comp.reshape(shape) for comp in get_components(case_model, group_name)][comp_idx]

                base_data = data_cache[group_name]["baseline"][comp_idx]
                ideal_data = data_cache[group_name]["ideal"][comp_idx]

                diff_ideal = np.abs(case_data - ideal_data)
                diff_base = np.abs(case_data - base_data)

                cols = [0, 1, 2] if group_name == "E-field" else [3, 4, 5]
                data_list = [case_data, diff_ideal, diff_base]
                titles = [f"|Case {ci}|", f"|Case {ci} − Ideal|", f"|Case {ci} − Baseline|"]

                for col_idx, col in enumerate(cols):
                    print(f"    Row {row}, plotting column {col_idx}...")
                    ax = axs[row, col]

                    # Colormap: case column uses original cmap, diff columns use 'bwr'
                    if col_idx == 0:  # raw case data
                        cmap_to_use = groups[group_name]["cmap"]
                    else:  # diff columns
                        cmap_to_use = "bwr"

                    m = ax.pcolormesh(xi, eta, data_list[col_idx], shading="auto", cmap=cmap_to_use)
                    ax.set_title(f"{group_name} ({comp_name})\n{titles[col_idx]}", fontsize=8)
                    format_ax(ax, base_model)
                    fig.colorbar(m, ax=ax, shrink=0.75)
            row += 1

    # make one big figure
    print("Saving figure...")
    os.makedirs(outdir, exist_ok=True)
    outfile = os.path.join(outdir, "big_6col_case_matrix.png")
    plt.tight_layout()
    fig.savefig(outfile, dpi=512, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"\nSaved giant comparison matrix to:\n{outfile}\n")


# run it
if __name__ == "__main__":

    direc = "/Users/clevenger/Projects/paper01/events/20230227/lompe/outputs/cases/"
    fn = "2023-02-27_083500.nc"
    outdir = os.path.join(direc, "diff_plots")

    plot_cases_matrix(direc, fn, outdir)
