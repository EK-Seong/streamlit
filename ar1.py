import pandas as pd
import numpy as np

def compute_ehats(file_path):
    """
    Computes ehats based on the given dataset.
    
    Parameters:
    - file_path: str, path to the CSV file containing the data.

    Returns:
    - ehats: numpy array of computed values.
    """
    # Step 1: Load the data
    infl = pd.read_csv(file_path)
    
    # Step 2: Calculate 'fe' (matrix of ecpi values)
    fe = pd.DataFrame({
        'ecpi0': infl['realized_cpi'] - infl['cpi0'],
        'ecpi1': infl['realized_cpi'] - infl['cpi1'],
        'ecpi2': infl['realized_cpi'] - infl['cpi2'],
        'ecpi3': infl['realized_cpi'] - infl['cpi3'],
        'ecpi4': infl['realized_cpi'] - infl['cpi4'],
    })
    
    # Convert 'fe' to a NumPy array
    fe = fe.to_numpy()
    
    # Step 3: Initialize an array for ehats
    ehats = np.full(fe.shape[1], np.nan)  # NaN array of size equal to the number of columns in 'fe'
    
    # Step 4: Loop through columns of 'fe' to compute ehats
    for i in range(fe.shape[1]):
        # Create Z with the current column and its lag
        lagged = np.roll(fe[:, i], 1)  # Lagged values (shift down by 1)
        lagged[0] = np.nan  # Set the first value to NaN for proper lagging
        
        Z = np.column_stack((fe[:, i], lagged))
        
        # Remove rows with NaN values (equivalent to rmmissing)
        Z = Z[~np.isnan(Z).any(axis=1)]
        
        # Extract X and Y
        Y = Z[:, 0]  # Current values
        X = Z[:, 1]  # Lagged values
        
        # Compute ehat using (X'X)^(-1) X'Y
        ehat =   (X.T @ Y)/(X.T @ X) * Y[-1]
        ehats[i] = ehat
    
    # Step 5: Return the results
    ehats = np.round(ehats,1)
    return ehats
