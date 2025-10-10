from unittest import result
import numpy as np
from scipy.sparse import csc_array
from scipy.sparse.linalg import lsmr
from scipy.linalg import svd
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error
from scipy.optimize import minimize
# from scipy.linalg import lu_factor, lu_solve #LU method does not seem to be suitable for this task
from scipy.optimize import nnls


def NNLS_solver_mass_spectra(normalized_bar_spectra, NIST_MASS_SPECTRA):
    #normalized_bar_spectra should be a (monodimentional) numpy array ordered by the mass/charge peaks
    # NIST_MASS_SPECTRA should be a dictionary with the format of the variable

    zero_intensities = {}

    # In order to this function to work, the input `normalized_bar_spectra` should be a normalized numpy array
    if not isinstance(normalized_bar_spectra, np.ndarray):
        normalized_bar_spectra = np.array(normalized_bar_spectra)
    if len(normalized_bar_spectra) != len(NIST_MASS_SPECTRA['Mass/Charge peaks']):
        raise ValueError("Input 'normalized_bar_spectra' must have the same length as the database.")
   
    # Extract molecule names, excluding 'Mass/Charge peaks'
    molecules = [key for key in NIST_MASS_SPECTRA.keys() if key != 'Mass/Charge peaks']

    
    # print("All molecules in database:")
    # for i, mol in enumerate(molecules):
    #     print(f"{i}: '{mol}'")
    #     if 'carbon' in mol.lower() or 'dioxide' in mol.lower():
    #         print(f"  -> FOUND CARBON DIOXIDE VARIANT: '{mol}'")

    # Build the coefficient matrix A
    # Each column corresponds to a molecule, and each row corresponds to a mass/charge peak
    # A transposition is done since list in python are stored in rows.
    A_list = []
    
    for mol in molecules:
        # print(f"DEBUG: {mol} spectrum length = {len(NIST_MASS_SPECTRA[mol])}, Mass/Charge peaks length = {len(NIST_MASS_SPECTRA['Mass/Charge peaks'])}")
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
    
    # print("A matrix row by row:")
    # for i, row in enumerate(A):
    #     print(f"Row {i}: {row}")
    #     # Right-hand side vector b
    
    b = normalized_bar_spectra

    # print("b vector:", b)
    # print("length of b:", len(b))
    
    x, residual = nnls(A, b)

    result = {}

    for i, mol in enumerate(molecules):
        result.update({mol: x[i]})

    print("NNLS residues:", residual)

    # print("Resulting coefficients:")
    # print("Resulting intensities:", result)
    return result

def SVD_solver_mass_spectra(normalized_bar_spectra, NIST_MASS_SPECTRA):

    # Solve the linear system Ax = b using the Moore-Penrose pseudoinverse computed via SVD.
    
    # Parameters:
    # A : array-like, shape (M, N)
    #     Coefficient matrix.
    # b : array-like, shape (M,) or (M, K)
    #     Dependent variable values.
    
    # Returns:
    # x : ndarray, shape (N,) or (N, K)
    #     Solution to the system Ax = b.

    zero_intensities = {}

    # In order to this function to work, the input `normalized_bar_spectra` should be a normalized numpy array
    if not isinstance(normalized_bar_spectra, np.ndarray):
        normalized_bar_spectra = np.array(normalized_bar_spectra)
    if len(normalized_bar_spectra) != len(NIST_MASS_SPECTRA['Mass/Charge peaks']):
        raise ValueError("Input 'normalized_bar_spectra' must have the same length as the database.")
   
    # Extract molecule names, excluding 'Mass/Charge peaks'
    molecules = [key for key in NIST_MASS_SPECTRA.keys() if key != 'Mass/Charge peaks']

    A_list = []
    
    for mol in molecules:
        # print(f"DEBUG: {mol} spectrum length = {len(NIST_MASS_SPECTRA[mol])}, Mass/Charge peaks length = {len(NIST_MASS_SPECTRA['Mass/Charge peaks'])}")
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

    b = np.array(normalized_bar_spectra, dtype=float)

    # Compute the SVD of A
    U, s, Vt = np.linalg.svd(A, full_matrices=False)
    
    # Calculate the pseudoinverse of the diagonal matrix of singular values
    s_inv = np.diag(np.where(s > 1e-12, 1.0 / s, 0.0))
    
    # Compute the pseudoinverse of A
    A_pinv = Vt.T @ s_inv @ U.T
    
    # Solve for x using the pseudoinverse
    x = A_pinv @ b
    return result

def tikhonov_regularization(NIST_MASS_SPECTRA, normalized_bar_spectra, alpha=1.0, L=None):

    # General Tikhonov regularization: min ||Ax - b||² + alpha * ||Lx||²
    
    # Parameters:
    # A : array-like
    #     Coefficient matrix.
    # b : array-like
    #     Right-hand side vector.
    # alpha : float
    #     Regularization parameter.
    # L : array-like, optional
    #     Regularization operator (identity by default).
    
    # Returns:
    # x : regularized solution.

    zero_intensities = {}

    # In order to this function to work, the input `normalized_bar_spectra` should be a normalized numpy array
    if not isinstance(normalized_bar_spectra, np.ndarray):
        normalized_bar_spectra = np.array(normalized_bar_spectra)
    if len(normalized_bar_spectra) != len(NIST_MASS_SPECTRA['Mass/Charge peaks']):
        raise ValueError("Input 'normalized_bar_spectra' must have the same length as the database.")

    # Extract molecule names, excluding 'Mass/Charge peaks'
    molecules = [key for key in NIST_MASS_SPECTRA.keys() if key != 'Mass/Charge peaks']

    # print("All molecules in database:")
    # for i, mol in enumerate(molecules):
    #     print(f"{i}: '{mol}'")
    #     if 'carbon' in mol.lower() or 'dioxide' in mol.lower():
    #         print(f"  -> FOUND CARBON DIOXIDE VARIANT: '{mol}'")

    # Build the coefficient matrix A
    # Each column corresponds to a molecule, and each row corresponds to a mass/charge peak
    # A transposition is done since list in python are stored in rows.
    A_list = []
    
    for mol in molecules:
        # print(f"DEBUG: {mol} spectrum length = {len(NIST_MASS_SPECTRA[mol])}, Mass/Charge peaks length = {len(NIST_MASS_SPECTRA['Mass/Charge peaks'])}")
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

    b = normalized_bar_spectra

    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    
    if L is None:
        L = np.eye(A.shape[1])
    
    # Solve: (A^T A + alpha * L^T L) x = A^T b
    
    left_side = A.T @ A + alpha * L.T @ L
    right_side = A.T @ b
    x = np.linalg.solve(left_side, right_side)
    return x

def regularized_solver_mass_spectra(normalized_bar_spectra, NIST_MASS_SPECTRA):
    
    def ridge_regression(A, b, alpha=1.0):

        # Solve regularized linear system using Ridge regression (L2 regularization).
        
        # Parameters:
        # A : array-like, shape (M, N)
        #     Coefficient matrix.
        # b : array-like, shape (M,)
        #     Dependent variable values.
        # alpha : float
        #     Regularization strength.
        
        # Returns:
        # x : ndarray, shape (N,)
        #     Regularized solution.

        A = np.array(A, dtype=float)
        b = np.array(b, dtype=float)
        
        # Using sklearn's Ridge regression
        ridge = Ridge(alpha=alpha, fit_intercept=False, solver='svd')
        ridge.fit(A, b)
        return ridge.coef_

    def lasso_regression(A, b, alpha=1.0):

        # Solve regularized linear system using Lasso regression (L1 regularization).
        
        # Parameters:
        # A : array-like, shape (M, N)
        #     Coefficient matrix.
        # b : array-like, shape (M,)
        #     Dependent variable values.
        # alpha : float
        #     Regularization strength.
        
        # Returns:
        # x : ndarray, shape (N,)
        #     Regularized solution.

        A = np.array(A, dtype=float)
        b = np.array(b, dtype=float)
        
        lasso = Lasso(alpha=alpha, fit_intercept=False, max_iter=10000)
        lasso.fit(A, b)

        return lasso.coef_

    def elastic_net(A, b, alpha=1.0, l1_ratio=0.5):

        # Solve regularized linear system using Elastic Net.
        
        # Parameters:
        # A : array-like, shape (M, N)
        #     Coefficient matrix.
        # b : array-like, shape (M,)
        #     Dependent variable values.
        # alpha : float
        #     Regularization strength.
        # l1_ratio : float
        #     Mixing parameter (0 = Ridge, 1 = Lasso).
        
        # Returns:
        # x : ndarray, shape (N,)
        #     Regularized solution.

        A = np.array(A, dtype=float)
        b = np.array(b, dtype=float)
        
        elastic = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, 
                            fit_intercept=False, max_iter=10000)
        elastic.fit(A, b)

        return elastic.coef_
    

            #     if method == 'ridge':
            #     model = Ridge(alpha=alpha, fit_intercept=False)
            # elif method == 'lasso':
            #     model = Lasso(alpha=alpha, fit_intercept=False, max_iter=10000)
            # elif method == 'elastic_net':
            #     model = ElasticNet(alpha=alpha, l1_ratio=0.5, fit_intercept=False, max_iter=10000)

 
            # alpha = 0.1
        
        # # Ridge regression
        # x_ridge = ridge_regression(A, b, alpha=alpha)
        
        # # Lasso regression
        # x_lasso = lasso_regression(A, b, alpha=alpha)
        
        # # Elastic Net
        # x_elastic = elastic_net(A, b, alpha=alpha, l1_ratio=0.5)

        return x_ridge

#def sparse_solver_mass_spectra(normalized_bar_spectra, NIST_MASS_SPECTRA):

#def iterative_LSQR_solver_mass_spectra(normalized_bar_spectra, NIST_MASS_SPECTRA):

def iterative_LSMR_solver_mass_spectra(normalized_bar_spectra, NIST_MASS_SPECTRA):
    
    zero_intensities = {}

    # In order to this function to work, the input `normalized_bar_spectra` should be a normalized numpy array
    if not isinstance(normalized_bar_spectra, np.ndarray):
        normalized_bar_spectra = np.array(normalized_bar_spectra)
    if len(normalized_bar_spectra) != len(NIST_MASS_SPECTRA['Mass/Charge peaks']):
        raise ValueError("Input 'normalized_bar_spectra' must have the same length as the database.")
   
    # Extract molecule names, excluding 'Mass/Charge peaks'
    molecules = [key for key in NIST_MASS_SPECTRA.keys() if key != 'Mass/Charge peaks']

    
    # print("All molecules in database:")
    # for i, mol in enumerate(molecules):
    #     print(f"{i}: '{mol}'")
    #     if 'carbon' in mol.lower() or 'dioxide' in mol.lower():
    #         print(f"  -> FOUND CARBON DIOXIDE VARIANT: '{mol}'")

    # Build the coefficient matrix A
    # Each column corresponds to a molecule, and each row corresponds to a mass/charge peak
    # A transposition is done since list in python are stored in rows.
    A_list = []
    for mol in molecules:
        # print(f"DEBUG: {mol} spectrum length = {len(NIST_MASS_SPECTRA[mol])}, Mass/Charge peaks length = {len(NIST_MASS_SPECTRA['Mass/Charge peaks'])}")
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
    A = csc_array(A_list).T  # Transpose to have molecules as columns
    
    # print("A matrix row by row:")
    # for i, row in enumerate(A):
    #     print(f"Row {i}: {row}")
    #     # Right-hand side vector b
    
    b = normalized_bar_spectra

    # print("b vector:", b)
    # print("length of b:", len(b))
    
    x, istop, itn, normr = lsmr(A, b)

    if istop != 7:
        print(f"LSMR finished with istop={istop}, itn={itn}, normr={normr}")
    else:
        print("LSMR ITN reached maxiter before the other stopping conditions were satisfied.")


    result = {}

    for i, mol in enumerate(molecules):
        result.update({mol: x[i]})

    print("NNLS residues:", residual)

    # print("Resulting coefficients:")
    # print("Resulting intensities:", result)
    return result
