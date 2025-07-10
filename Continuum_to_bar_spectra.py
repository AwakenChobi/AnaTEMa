import numpy as np

def Continuum_to_bar_spectra(x,y,database):
    #substract background
    #The first approach that it has been taken is to assume a linear increment towards lower values of q/m
    #IMPORTANT this code is only compatible with .sac quadstar files, but if you detect a different behavior,
    #feel free to adapt this computation

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

    for i in database['Mass/Charge peaks']: #database should have the format of the variable stored in mass_spectra_database.py
        mask= x[np.where((x > i-0.08) & (x < i+0.08))] #adjust the range to consider max value of y.
        if np.max(y[mask]) > (6.5*10**-6):             #adjust the minimun value of y to consider a peak
            y_bars.append(np.max(y[mask]))
        else:
            y_bars.append(0)
    
    return np.array(x_bars), np.array(y_bars)