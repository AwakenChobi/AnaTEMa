import numpy as np
from mass_spectra_database import NIST_MASS_SPECTRA

def find_peak_contributions():
    """
    Analyzes NIST_MASS_SPECTRA to find:
    - Isolated peaks (only one molecule contributes)
    - Pair contributions (exactly two molecules contribute)
    - Triple contributions (exactly three molecules contribute)
    - Higher order contributions (4-20 molecules contribute)
    """
    
    mass_charges = NIST_MASS_SPECTRA['Mass/Charge peaks']
    molecule_names = [name for name in NIST_MASS_SPECTRA.keys() if name != 'Mass/Charge peaks']
    
    print("="*60)
    print("PEAK CONTRIBUTION ANALYSIS")
    print("="*60)
    
    peaks_by_contributors = {}
    for i in range(1, 40): 
        peaks_by_contributors[i] = []
    
    for i, mz in enumerate(mass_charges):
        contributing_molecules = []
        
        for molecule in molecule_names:
            intensity = NIST_MASS_SPECTRA[molecule][i]
            if intensity > 0:  # Non-zero contribution
                contributing_molecules.append((molecule, intensity))
        
        num_contributors = len(contributing_molecules)
        
        if 1 <= num_contributors <= 40:
            peaks_by_contributors[num_contributors].append((mz, i, contributing_molecules))

    # Print results for each category
    for num_contrib in range(1, 40):
        peaks = peaks_by_contributors[num_contrib]
        
        if peaks:
            if num_contrib == 1:
                print(f"\n🔍 ISOLATED PEAKS ({num_contrib} molecule contributes):")
            elif num_contrib == 2:
                print(f"\n🔍 PAIR CONTRIBUTIONS ({num_contrib} molecules contribute):")
            elif num_contrib == 3:
                print(f"\n🔍 TRIPLE CONTRIBUTIONS ({num_contrib} molecules contribute):")
            else:
                print(f"\n🔍 {num_contrib}-MOLECULE CONTRIBUTIONS ({num_contrib} molecules contribute):")
            
            print("-" * 60)
            
            for mz, idx, contributors in peaks:
                print(f"m/z = {mz:4.1f} (index {idx:2d}):")
                for molecule, intensity in contributors:
                    print(f"    {molecule:<30} (intensity: {intensity:.4f})")
                print()
    
    # Summary statistics
    print("\n📊 SUMMARY:")
    print("-" * 30)
    print(f"Total mass/charge values: {len(mass_charges)}")
    
    for num_contrib in range(1, 21):
        count = len(peaks_by_contributors[num_contrib])
        if count > 0:
            if num_contrib == 1:
                print(f"Isolated peaks (1 molecule): {count}")
            elif num_contrib == 2:
                print(f"Pair contributions (2 molecules): {count}")
            elif num_contrib == 3:
                print(f"Triple contributions (3 molecules): {count}")
            else:
                print(f"{num_contrib}-molecule contributions: {count}")
    
    very_high_order = 0
    max_contributors = 0
    max_contrib_peak = None
    
    for i, mz in enumerate(mass_charges):
        contributors = sum(1 for molecule in molecule_names if NIST_MASS_SPECTRA[molecule][i] > 0)
        if contributors > 40:
            very_high_order += 1
        if contributors > max_contributors:
            max_contributors = contributors
            max_contrib_peak = mz
    
    if very_high_order > 0:
        print(f"Very high order contributions (>20): {very_high_order}")
    
    print(f"Maximum contributors at any peak: {max_contributors} (at m/z = {max_contrib_peak})")
    
    return peaks_by_contributors

def find_zero_contributions():
    """
    Find mass/charge values where NO molecules contribute (all zeros)
    """
    mass_charges = NIST_MASS_SPECTRA['Mass/Charge peaks']
    molecule_names = [name for name in NIST_MASS_SPECTRA.keys() if name != 'Mass/Charge peaks']
    
    zero_peaks = []
    
    for i, mz in enumerate(mass_charges):
        all_zero = True
        for molecule in molecule_names:
            if NIST_MASS_SPECTRA[molecule][i] > 0:
                all_zero = False
                break
        
        if all_zero:
            zero_peaks.append((mz, i))
    
    print("\n🚫 ZERO CONTRIBUTION PEAKS (no molecules contribute):")
    print("-" * 50)
    if zero_peaks:
        for mz, idx in zero_peaks:
            print(f"m/z = {mz:4.1f} (index {idx:2d}): ALL ZERO")
    else:
        print("No zero-contribution peaks found.")
    
    return zero_peaks

def analyze_contribution_distribution():
    """
    Analyze the distribution of contributors across all peaks
    """
    mass_charges = NIST_MASS_SPECTRA['Mass/Charge peaks']
    molecule_names = [name for name in NIST_MASS_SPECTRA.keys() if name != 'Mass/Charge peaks']
    
    contributor_counts = []
    
    for i, mz in enumerate(mass_charges):
        contributors = sum(1 for molecule in molecule_names if NIST_MASS_SPECTRA[molecule][i] > 0)
        contributor_counts.append(contributors)
    
    print("\n📈 CONTRIBUTION DISTRIBUTION:")
    print("-" * 40)
    print(f"Average contributors per peak: {np.mean(contributor_counts):.2f}")
    print(f"Median contributors per peak: {np.median(contributor_counts):.2f}")
    print(f"Min contributors: {np.min(contributor_counts)}")
    print(f"Max contributors: {np.max(contributor_counts)}")
    print(f"Standard deviation: {np.std(contributor_counts):.2f}")
    
    return contributor_counts

# if __name__ == "__main__":
#     peaks_by_contributors = find_peak_contributions()
#     zeros = find_zero_contributions()
#     distribution = analyze_contribution_distribution()
    
#     print("\n" + "="*60)
#     print("ANALYSIS COMPLETE")
#     print("="*60)

# Print molecules that contributes in each peak
mass_charges = NIST_MASS_SPECTRA['Mass/Charge peaks']
for mz in mass_charges:
    print(f"\n M/Z = {mz}:")
    for molecule in NIST_MASS_SPECTRA.keys():
        if molecule != 'Mass/Charge peaks':
            for i in NIST_MASS_SPECTRA['Mass/Charge peaks']:
                intensity = NIST_MASS_SPECTRA[molecule][i-2]
                if intensity > 0:
                    if mz == i:
                        print(f"    {molecule:<30} (intensity: {intensity:.4f})")