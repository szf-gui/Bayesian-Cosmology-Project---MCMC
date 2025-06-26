import getdist
from getdist import plots, MCSamples
import numpy as np
import os

# --- Configuration ---
# Comparing the three "alone" runs that you have completed.
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

# Define the specific parameters we want to plot
params_to_plot = ['omegam', 'H0']

# --- Loading and Analysis ---
print("Loading chains for comparison...")

samples_list = []
loaded_legends = []

for root, legend in zip(chain_roots, legend_labels):
    print(f"\n--> Loading: {legend} ({root})")
    try:
        samples = None
        if root == 'planck_chains_native':
            planck_file = 'planck_chains_native.1.txt'
            if os.path.exists(planck_file):
                print(f"    Using manual loader for {planck_file}...")
                planck_all_column_names = [
                    'weight', 'minuslogpost', 'ombh2', 'omch2', 'H0', 'tau', 'As', 'ns', 
                    'A_planck', 'chi2__CMB', 'minuslogprior', 'minuslogprior__0', 'chi2', 
                    'chi2__planck_2018_highl_plik.TTTEEE_lite_native', 
                    'chi2__planck_2018_lowl.TT', 'chi2__planck_2018_lowl.EE', 
                    'chi2__planck_2018_lensing.native']
                data = np.loadtxt(planck_file)
                samples = MCSamples(samples=data, names=planck_all_column_names)
                samples.removeBurn(0.3)
                samples.updateBaseStatistics()
            else:
                print(f"    Warning: Could not find {planck_file}. Skipping.")
        else:
            if os.path.exists(root + '.1.txt'):
                 print(f"    Using standard loader for {root}...")
                 samples = getdist.loadMCSamples(root, settings={'ignore_rows': 0.3})
            else:
                print(f"    Warning: Could not find chain file for root '{root}'. Skipping.")
        
        if samples:
            # --- CORRECTED: Calculate derived Omega_m parameter explicitly ---
            # Get the list of parameter names in the order they appear in the samples
            p_names_list = [p.name for p in samples.getParamNames().names]
            
            # Find the column index for each parameter we need
            h0_index = p_names_list.index('H0')
            ombh2_index = p_names_list.index('ombh2')
            omch2_index = p_names_list.index('omch2')

            # Get the raw numpy array of all samples
            all_samples_array = samples.samples

            # Extract the columns of data using their index
            H0_vals = all_samples_array[:, h0_index]
            ombh2_vals = all_samples_array[:, ombh2_index]
            omch2_vals = all_samples_array[:, omch2_index]
            
            # Perform the calculation
            h = H0_vals / 100.0
            omega_m_values = (ombh2_vals + omch2_vals) / h**2
            samples.addDerived(omega_m_values, name='omegam', label=r'\Omega_m')
            # ------------------------------------------------------------------
            
            samples_list.append(samples)
            loaded_legends.append(legend)
            print(f"    Successfully loaded and derived Omega_m.")
        else:
            print(f"    Failed to load samples.")

    except Exception as e:
        print(f"    An error occurred while loading '{root}': {e}. Skipping.")

if not samples_list:
    print("\nNo valid chains were loaded. Exiting.")
    exit()

print(f"\nSuccessfully loaded {len(samples_list)} chains for comparison.")

# --- Generate Comparison Plot ---
print("\n\n" + "="*60)
print("--- Generating Omega_m vs H0 Triangle Plot ---")

g = plots.get_subplot_plotter(width_inch=8)
g.triangle_plot(samples_list, params=params_to_plot, filled=True, legend_labels=loaded_legends)

plot_filename = "omegam_H0_comparison.png"
g.export(plot_filename)

print(f"Comparison plot saved as '{plot_filename}'")
print("\nAnalysis complete.")
