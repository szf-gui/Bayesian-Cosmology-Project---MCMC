import getdist
from getdist import plots
import os

# --- Configuration ---
# List the chain roots for all the analyses you want to compare.
# Make sure the paths and prefixes match the 'output' field in your YAML files.
# We start with your original Planck-only run and add the new ones.
chain_roots = [
    'planck_chains_native',         # Your original Planck-only run
    'chains/desi_alone',
    'chains/pantheon_plus_alone',
    'chains/combined_planck_desi_sn'
]

# These are the labels that will appear in the plot legend.
legend_labels = [
    'Planck 2018',
    'DESI DR2 BAO',
    'Pantheon+',
    'Planck + DESI + Pantheon+'
]

# The list of base parameters you want to see on the plot.
params_to_plot = ['ombh2', 'omch2', 'H0', 'tau', 'As', 'ns']

# --- Loading and Analysis ---
print("Loading chains for comparison...")

samples_list = []
for root in chain_roots:
    # Check if the chain file exists before trying to load
    # Assumes the first chain is e.g. root + '.1.txt'
    if not os.path.exists(root + '.1.txt'):
        print(f"Warning: Chain file for root '{root}' not found. Skipping.")
        continue

    # Use the high-level loader, which is more robust
    # We set burn-in fraction via the settings dictionary
    try:
        # Note: For your older getdist version, you may need a different loader
        # if this fails, but loadMCSamples is the standard.
        samples = getdist.loadMCSamples(root, settings={'ignore_rows': 0.3})
        if samples:
            samples_list.append(samples)
        else:
            print(f"Warning: Failed to load samples for root '{root}'. Skipping.")
    except Exception as e:
        print(f"Error loading samples for root '{root}': {e}. Skipping.")

if not samples_list:
    print("No valid chains were loaded. Exiting.")
    exit()

print(f"\nSuccessfully loaded {len(samples_list)} chains.")

# --- Print Comparison of Numerical Results ---
print("\n\n" + "="*60)
print("   Comparison of Marginalized Parameter Constraints (68% C.L.)")
print("="*60)

for i, s in enumerate(samples_list):
    print(f"\n--- {legend_labels[i]} ---")
    # For older getdist, getMargeStats() is the reliable method
    stats = s.getMargeStats()
    for p in params_to_plot:
        param_stats = stats.parWithName(p)
        if param_stats:
            mean = param_stats.mean
            err = param_stats.err
            print(f"  {p:<10} = {mean:.4g} +/- {err:.2g}")

# --- Generate Comparison Plot ---
print("\n\n" + "="*60)
print("--- Generating Comparison Triangle Plot ---")

g = plots.get_subplot_plotter(width_inch=12)

# The key step: triangle_plot can accept a list of MCSamples objects
g.triangle_plot(samples_list, params=params_to_plot, filled=True, legend_labels=legend_labels)

plot_filename = "comparison_triangle_plot.png"
g.export(plot_filename)

print(f"Comparison plot saved as '{plot_filename}'")
print("\nComparison complete.")