import getdist
from getdist import plots, MCSamples
import numpy as np
import os

# --- Configuration ---
chain_roots = [
    'planck_chains_native',
    'chains/desi_alone',
    'chains/pantheon_plus_alone'
]

legend_labels = [
    'Planck 2018 Only',
    'DESI DR2 BAO Only',
    'Pantheon+ Only'
]

# The list of base parameters you want to see on the plot.
params_to_plot = ['ombh2', 'omch2', 'H0', 'tau', 'As', 'ns']

# --- Loading and Analysis ---
print("Loading chains for comparison...")

samples_list = []
for root, legend in zip(chain_roots, legend_labels):
    print(f"\n--> Loading: {legend} ({root})")
    try:
        samples = None
        # SPECIAL LOADER FOR THE ORIGINAL PLANCK CHAIN
        if root == 'planck_chains_native':
            planck_file = 'planck_chains_native.1.txt'
            if os.path.exists(planck_file):
                print(f"    Using manual loader for {planck_file}...")
                
                # The full, correct list of all 17 columns in your file
                planck_all_column_names = [
                    'weight', 'minuslogpost', 'ombh2', 'omch2', 'H0', 'tau', 'As', 
                    'ns', 'A_planck', 'chi2__CMB', 'minuslogprior', 'minuslogprior__0', 
                    'chi2', 'chi2__planck_2018_highl_plik.TTTEEE_lite_native', 
                    'chi2__planck_2018_lowl.TT', 'chi2__planck_2018_lowl.EE', 
                    'chi2__planck_2018_lensing.native']
                
                data = np.loadtxt(planck_file)

                # Give getdist the full data and all the names.
                # It will automatically identify 'weight' and 'minuslogpost'.
                samples = MCSamples(samples=data, names=planck_all_column_names)
                samples.removeBurn(0.3) # Manually remove burn-in
                samples.updateBaseStatistics()
            else:
                print(f"    Warning: Could not find {planck_file}. Skipping.")
        
        # STANDARD LOADER FOR ALL OTHER CHAINS
        else:
            if os.path.exists(root + '.1.txt'):
                 print(f"    Using standard loader for {root}...")
                 samples = getdist.loadMCSamples(root, settings={'ignore_rows': 0.3})
            else:
                print(f"    Warning: Could not find chain file for root '{root}'. Skipping.")
        
        if samples:
            samples_list.append(samples)
            print(f"    Successfully loaded.")
        else:
            print(f"    Failed to load samples for root '{root}'.")

    except Exception as e:
        print(f"    An error occurred while loading '{root}': {e}. Skipping.")

if not samples_list:
    print("\nNo valid chains were loaded. Exiting.")
    exit()

print(f"\nSuccessfully loaded {len(samples_list)} chains for comparison.")

# --- Print Comparison of Numerical Results ---
print("\n\n" + "="*60)
print("   Comparison of Marginalized Parameter Constraints (68% C.L.)")
print("="*60)

for i, s in enumerate(samples_list):
    # THIS LINE IS NOW CORRECTED
    print(f"\n--- {legend_labels[i]} ---")
    stats = s.getMargeStats()
    for p in params_to_plot:
        param_stats = stats.parWithName(p)
        if param_stats:
            mean = param_stats.mean
            err = param_stats.err
            print(f"  {p:<10} = {mean:.4g} +/- {err:.2g}")
        else:
            print(f"  {p:<10} = Not constrained by this dataset")

# --- Generate Comparison Plot ---
print("\n\n" + "="*60)
print("--- Generating Comparison Triangle Plot ---")

g = plots.get_subplot_plotter(width_inch=12)
g.triangle_plot(samples_list, params=params_to_plot, filled=True, legend_labels=legend_labels)

plot_filename = "comparison_triangle_plot.png"
g.export(plot_filename)

print(f"Comparison plot saved as '{plot_filename}'")
print("\nComparison complete.")
