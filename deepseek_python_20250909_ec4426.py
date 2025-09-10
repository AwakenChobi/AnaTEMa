import numpy as np
from scipy.optimize import nnls
import matplotlib.pyplot as plt

# Load and parse the mass spectrometry data
def load_mass_data(filename):
    data = np.loadtxt(filename, skiprows=1)
    masses = data[:, 0]
    intensities = data[:, 1:]
    
    # Ignore m/z=1 (first row) as it doesn't provide usable information
    return masses[1:], intensities[1:]

# Extract molecular spectra from the database
def get_molecular_spectra():
    # Import the actual database
    from mass_spectra_database import NIST_MASS_SPECTRA
    
    molecules = {}
    for key, spectrum in NIST_MASS_SPECTRA.items():
        if key != 'Mass/Charge peaks':
            # Skip m/z=1 (first element) and use from m/z=2 onward
            molecules[key] = spectrum[1:]  # Use from index 1 onward
    
    return molecules

# Main analysis function
def analyze_mass_spectrometry():
    # Load data, ignoring m/z=1
    masses, intensities = load_mass_data('masas.txt')
    
    # Get molecular spectra from the database
    molecules = get_molecular_spectra()
    molecule_names = list(molecules.keys())
    
    # Create the design matrix A (masses × molecules)
    # Pad or truncate database spectra to match the data length
    max_mass_idx = len(masses)
    A = np.zeros((max_mass_idx, len(molecule_names)))
    
    for i, name in enumerate(molecule_names):
        spec = molecules[name]
        # Handle cases where database spectrum is shorter than our data
        if len(spec) < max_mass_idx:
            padded_spec = np.zeros(max_mass_idx)
            padded_spec[:len(spec)] = spec
            A[:, i] = padded_spec
        else:
            A[:, i] = spec[:max_mass_idx]
    
    # Analyze each cycle
    num_cycles = intensities.shape[1]
    concentrations = np.zeros((len(molecule_names), num_cycles))
    residuals = np.zeros(num_cycles)
    
    for i in range(num_cycles):
        # Get the intensity vector for this cycle
        b = intensities[:, i]
        
        # Solve using NNLS
        x, residual = nnls(A, b)
        concentrations[:, i] = x
        residuals[i] = residual
        
        # Optional: Print progress
        if (i+1) % 20 == 0:
            print(f"Processed cycle {i+1}/{num_cycles}, residual: {residual:.4e}")
    
    # Analyze results
    print("\n=== Analysis Results ===")
    print("Average concentrations across all cycles:")
    avg_concentrations = np.mean(concentrations, axis=1)
    
    # Sort molecules by average concentration
    sorted_indices = np.argsort(avg_concentrations)[::-1]
    
    for idx in sorted_indices:
        if avg_concentrations[idx] > 1e-10:  # Only show molecules with significant concentration
            print(f"{molecule_names[idx]}: {avg_concentrations[idx]:.4e}")
    
    # Plot results
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Residuals across cycles
    plt.subplot(2, 2, 1)
    plt.plot(residuals)
    plt.xlabel('Cycle')
    plt.ylabel('Residual')
    plt.title('NNLS Residuals Across Cycles')
    plt.grid(True)
    
    # Plot 2: Concentrations over time for the top 5 most abundant molecules
    plt.subplot(2, 2, 2)
    top_n = min(5, len(molecule_names))
    for i in range(top_n):
        idx = sorted_indices[i]
        plt.plot(concentrations[idx, :], label=molecule_names[idx])
    plt.xlabel('Cycle')
    plt.ylabel('Concentration')
    plt.title('Top 5 Molecule Concentrations Over Time')
    plt.legend()
    plt.grid(True)
    
    # Plot 3: Average concentration distribution
    plt.subplot(2, 2, 3)
    significant_indices = [i for i in sorted_indices if avg_concentrations[i] > 1e-10]
    plt.bar(range(len(significant_indices)), avg_concentrations[significant_indices])
    plt.xticks(range(len(significant_indices)), [molecule_names[i] for i in significant_indices], rotation=45, ha='right')
    plt.ylabel('Average Concentration')
    plt.title('Average Concentration Distribution')
    plt.tight_layout()
    
    # Plot 4: Example spectrum reconstruction for a specific cycle
    plt.subplot(2, 2, 4)
    cycle_to_plot = num_cycles // 2  # Middle cycle
    reconstructed = A @ concentrations[:, cycle_to_plot]
    plt.plot(masses, intensities[:, cycle_to_plot], 'b-', label='Measured')
    plt.plot(masses, reconstructed, 'r--', label='Reconstructed')
    plt.xlabel('m/z')
    plt.ylabel('Intensity')
    plt.title(f'Spectrum Reconstruction (Cycle {cycle_to_plot})')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('mass_spec_analysis.png', dpi=300)
    plt.show()
    
    return concentrations, molecule_names, residuals

# Run the analysis
if __name__ == "__main__":
    concentrations, molecule_names, residuals = analyze_mass_spectrometry()
    
    # Additional analysis: Identify dominant molecules in each cycle
    print("\n=== Dominant Molecules in Each Cycle ===")
    for cycle in range(0, concentrations.shape[1], 20):  # Print every 20th cycle
        dominant_idx = np.argmax(concentrations[:, cycle])
        print(f"Cycle {cycle}: {molecule_names[dominant_idx]} (conc: {concentrations[dominant_idx, cycle]:.4e})")