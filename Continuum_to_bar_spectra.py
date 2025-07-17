import numpy as np

def continuum_to_bar_spectra(x,y,database):
    #substract background
    #The first approach that it has been taken is to assume a linear increment towards lower values of q/m
    #IMPORTANT this code is only compatible with .sac quadstar files, but if you detect a different behavior,
    #feel free to adapt this computation

    x = np.array(x)
    y = np.array(y)
    mask1= np.where(x < 10, True, False)
    mask2= np.where(x > 45, True, False)

    # For mask1
    y1 = y[mask1]
    x1 = x[mask1]
    idx1 = np.argmin(y1)
    min_y_1 = y1[idx1]
    min_x_1 = x1[idx1]

    # For mask2
    y2 = y[mask2]
    x2 = x[mask2]
    idx2 = np.argmin(y2)
    min_y_2 = y2[idx2]
    min_x_2 = x2[idx2]

    log_y1 = np.log10(min_y_1)
    log_y2 = np.log10(min_y_2)

    # Calculate the slope (m) and intercept (b) for the linear fit
    slope = (log_y2 - log_y1) / (min_x_2 - min_x_1)
    intercept = log_y1 - slope * min_x_1

    background = 10**(slope * x + intercept)

    # Subtract the background from the original y values
    y_corrected = y - background

    y_bars = []
    x_bars = database['Mass/Charge peaks']

    # Check if the database has the size of the spectra

    for i in database['Mass/Charge peaks']: # database should have the format of the variable stored in mass_spectra_database.py
        mask = (x > i-0.08) & (x < i+0.08)  # boolean mask with x values
        if np.any(mask) and np.max(y_corrected[mask]) > (0*10**-13): #adjust the threshold (it is better to keep it low otherwise it could cause problems solving the system)
            y_bars.append(np.max(y_corrected[mask]))
        else:
            y_bars.append(0)
            
    # Normalize the y_bars values
    print("Max value of y_bars before normalization:", np.max(y_bars))
    if np.max(y_bars) > 0:
        normalized_y_bars = y_bars / np.max(y_bars)
    else:
        normalized_y_bars = y_bars

    # Ensure x_bars is a numpy array
    x_bars = np.array(x_bars)

    return x_bars, y_bars, normalized_y_bars