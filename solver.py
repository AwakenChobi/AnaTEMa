from unittest import result
import numpy as np
# from scipy.linalg import lu_factor, lu_solve #LU method does not seem to be suitable for this task
from scipy.optimize import nnls

def NNLS_solver_mass_spectra_etanol(normalized_bar_spectra, NIST_MASS_SPECTRA):
    #normalized_bar_spectra should be a (monodimentional) numpy array ordered by the mass/charge peaks
    # NIST_MASS_SPECTRA should be a dictionary with the format of the variable

    # Zeros intensities in normalized_bar_spectra: q/m = 3, 4, 5, 6, 7, 8, 9, 50, 51
    zero_intensities = {3, 4, 5, 6, 7, 8, 9, 50, 51}

    # In order to this function to work, the input `normalized_bar_spectra` should be a normalized numpy array
    if not isinstance(normalized_bar_spectra, np.ndarray):
        normalized_bar_spectra = np.array(normalized_bar_spectra)
    if len(normalized_bar_spectra) != len(NIST_MASS_SPECTRA['Mass/Charge peaks']):
        raise ValueError("Input 'normalized_bar_spectra' must have the same length as the database.")
   
    # Extract molecule names, excluding 'Mass/Charge peaks'
    molecules = [key for key in NIST_MASS_SPECTRA.keys() if key != 'Mass/Charge peaks']

    
    # Build the coefficient matrix A
    # Each column corresponds to a molecule, and each row corresponds to a mass/charge peak
    # A transposition is done since list in python are stored in rows.
    A_list = []
    for mol in molecules:
        print(f"DEBUG: {mol} spectrum length = {len(NIST_MASS_SPECTRA[mol])}, Mass/Charge peaks length = {len(NIST_MASS_SPECTRA['Mass/Charge peaks'])}")
        if mol in zero_intensities:
            # If the molecule is in zero_intensities, we set its spectrum to zero
            spectrum = np.zeros(len(NIST_MASS_SPECTRA['Mass/Charge peaks']))
        else:
            # Otherwise, we extract the spectrum from the database
            if mol not in NIST_MASS_SPECTRA:
                raise KeyError(f"Molecule '{mol}' not found in the database.")
            if len(NIST_MASS_SPECTRA[mol]) != len(NIST_MASS_SPECTRA['Mass/Charge peaks']):
                raise ValueError(f"Spectrum for '{mol}' does not match the length of 'Mass/Charge peaks'.")
            spectrum = NIST_MASS_SPECTRA[mol]
        A_list.append(spectrum)
    A = np.array(A_list).T  # Transpose to have molecules as columns
    
    print("A matrix row by row:")
    for i, row in enumerate(A):
        print(f"Row {i}: {row}")
        # Right-hand side vector b
    
    b = normalized_bar_spectra

    print("b vector:", b)
    print("length of b:", len(b))
    
    # Perform LU factorization and solve
    #lu, piv = lu_factor(A)
    #x = lu_solve((lu, piv), b)

    #x = np.linalg.solve(A, b)

    # Create result dictionary
    #result = {}
    #for i, mol in enumerate(molecules):
    #    result[mol] = x[i]

    ########################################### PLACEHOLDER FOR THE RESULT ###########################################
    
    x, residual = nnls(A, b)

    result = {}

    for i, mol in enumerate(molecules):
        result.update({mol: x[i]})

    print("NNLS residues:", residual)

    print("Resulting coefficients:")
    print("Resulting intensities:", result)
    return result