import getdist
from getdist import plots, MCSamples
import numpy as np
import os

# --- Configuration ---
chain_file = 'planck_chains_native.1.txt'
burn_in_fraction = 0.3

# This dictionary maps the parameter names found in your file
# to the pretty LaTeX labels used in the plot legends.
label_dict = {
    'ombh2': r'\Omega_b h^2',
    'omch2': r'\Omega_c h^2',
    'H0': r'H_0',
    'tau': r'\tau',
    'ns': r'n_s',
    'As': r'A_s'
}

try:
    # --- Step 1: Read the header to get all column names ---
    with open(chain_file, 'r') as f:
        header = f.readline().strip()
        if not header.startswith('#'):
            raise ValueError("Chain file is missing a header row starting with '#'.")
        all_column_names = header[1:].strip().split()

    # --- Step 2: Define the list of parameters to plot ---
    base_params_to_plot = ['ombh2', 'omch2', 'H0', 'tau', 'As', 'ns']

    # --- Step 3: Load the data and create the MCSamples object ---
    print(f"Reading from: '{chain_file}'...")
    data = np.loadtxt(chain_file)
    samples = MCSamples(samples=data, names=all_column_names, labels=[label_dict.get(name, name) for name in all_column_names])
    rows_to_ignore = int(burn_in_fraction * len(samples.samples))
    samples.removeBurn(rows_to_ignore)
    samples.updateBaseStatistics()
    print(f"Successfully loaded and processed {len(samples.samples)} samples.")

except Exception as e:
    print("\n--- AN ERROR OCCURRED ---")
    print(f"Error details: {e}")
    exit()

# --- Analysis & Plotting with Detailed Numerical Output ---

# This provides a clean summary table of the results.
print("\n\n" + "="*50)
print("   Marginalized Parameter Constraints (Summary Table)")
print("="*50)
print(samples.getMargeStats())


# This provides a more detailed, value-by-value breakdown.
print("\n\n" + "="*50)
print("      Detailed Parameter Values (68% Confidence)")
print("="*50)
for p_name in base_params_to_plot:
    stats = samples.getMargeStats().parWithName(p_name)
    if stats:
        mean = stats.mean
        err = stats.err
        lower_limit_68 = stats.limits[0].lower
        upper_limit_68 = stats.limits[0].upper
        
        # Use '.4g' for general-purpose formatting to handle small numbers like As
        print(f"\nParameter: {stats.label}")
        print(f"  - Mean:           {mean:.4g}")
        print(f"  - Std. Dev.:      {err:.4g}")
        print(f"  - 68% Lower:      {lower_limit_68:.4g}")
        print(f"  - 68% Upper:      {upper_limit_68:.4g}")
        print(f"  -> Publication Format: {p_name} = {mean:.3g} +/- {err:.3g}")
    else:
        print(f"\nCould not get stats for parameter: {p_name}")

print("\n\n" + "="*50)
print("--- Generating Triangle Plot ---")
g = plots.get_subplot_plotter(width_inch=10)
g.triangle_plot(samples, params=base_params_to_plot, filled=True, legend_loc='best')

plot_filename = "planck_chains_native_triangle_plot.png"
g.export(plot_filename)
print(f"Triangle plot saved as '{plot_filename}'")
print("\nAnalysis complete.")
