import getdist
from getdist import plots
import os

# --- Configuration ---
# 1. SET THE PATH TO THE CHAIN YOU WANT TO ANALYZE
# This should be the 'output' prefix from your YAML file.
chain_root = 'chains/combined_planck_desi_sn_w0waCDM_FAST1'

# 2. LIST THE PARAMETERS YOU WANT TO PLOT
# These should match the names in your YAML file.
params_to_plot = ['ombh2', 'omch2', 'H0', 'tau', 'As', 'ns', 'w', 'wa']


# --- Loading ---
print(f"Loading chain: {chain_root}")
try:
    # Use the standard getdist loader. It should find the .txt and .paramnames files.
    samples = getdist.loadMCSamples(chain_root, settings={'ignore_rows': 0.3})
    if not samples:
         raise ValueError("loadMCSamples returned None. Check chain path and files.")
    print(f"Successfully loaded {len(samples.samples)} samples after burn-in.")
except Exception as e:
    print(f"Error: Could not load chains for '{root}'.")
    print(f"Details: {e}")
    exit()

# --- Get Numerical Results ---
print("\n\n" + "="*50)
print("   Marginalized Parameter Constraints")
print("="*50)
# For your older getdist version, printing the MargeStats object directly gives a summary table
print(samples.getMargeStats())


# --- Generate Triangle Plot ---
print("\n\n" + "="*50)
print("--- Generating Triangle Plot ---")

g = plots.get_subplot_plotter(width_inch=14) # Made the plot a bit wider for the extra parameters
g.triangle_plot(samples, params=params_to_plot, filled=True, legend_loc='upper right')

# Create a unique filename for the plot
plot_filename = f"{chain_root}_triangle.png"
g.export(plot_filename)

print(f"Plot saved as '{plot_filename}'")
print("\nAnalysis complete.")
