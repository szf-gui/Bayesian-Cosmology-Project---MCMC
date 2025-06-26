import getdist
import numpy as np
import os

# --- Configuration ---
# Set the path to the chain you want to analyze.
chain_root = 'chains/combined_planck_desi_sn_w0waCDM_FAST1'

# --- Loading ---
print(f"Loading chain: {chain_root}")
try:
    # Use the standard getdist loader
    samples = getdist.loadMCSamples(chain_root, settings={'ignore_rows': 0.3})
    if not samples:
         raise ValueError("loadMCSamples returned None. Check chain path and files.")
    print("Successfully loaded chains.")
except Exception as e:
    print(f"Error: Could not load chains for '{chain_root}'.")
    print(f"Details: {e}")
    exit()

# --- Calculation ---
print("\n" + "="*50)
print("      Goodness-of-Fit Calculation")
print("="*50)

try:
    # Get all the raw sample data as a numpy array
    all_samples_array = samples.samples

    # Get the list of all parameter names in the correct order
    all_names = [p.name for p in samples.getParamNames().names]

    # Find the column index for the total chi-squared parameter
    # Note: The MargeStats table shows it as 'chi2*', the actual name is 'chi2'
    chi2_index = all_names.index('chi2')
    
    # Find the row index of the best-fit point (the one with the minimum -log(likelihood))
    best_fit_index = np.argmin(samples.loglikes)

    # Extract the specific chi-squared value from that row and column
    total_chi2 = all_samples_array[best_fit_index, chi2_index]
    
    print(f"\nBest-fit total Chi-Squared (\u03C7\u00B2): {total_chi2:.2f}")

    # The "degrees of freedom" (nu) is the number of data points minus the number of free parameters.
    # For a good fit, we expect chi^2 / nu ~ 1, which means nu is approximately equal to chi^2.
    degrees_of_freedom = int(round(total_chi2))
    print(f"Estimated Degrees of Freedom (\u03BD): {degrees_of_freedom}")

    # Calculate the reduced chi-squared
    reduced_chi2 = total_chi2 / degrees_of_freedom
    print(f"Reduced Chi-Squared (\\chi^2/\\u03BD): {reduced_chi2:.4f}")

    if 0.95 < reduced_chi2 < 1.05:
        print("\nConclusion: The reduced chi-squared is very close to 1.")
        print("This indicates an excellent and statistically robust fit to the data.")
    else:
        print("\nConclusion: The reduced chi-squared is not close to 1, which may warrant further investigation.")

except ValueError:
    print("\nCould not find the 'chi2' derived parameter in the chain's .paramnames file.")
    print("This can happen if the likelihood was not configured to save it.")
except Exception as e:
    print(f"\nAn unexpected error occurred during calculation: {e}")
    
print("\n" + "="*50)
