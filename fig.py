import numpy as np
import matplotlib.pyplot as plt

# Load the data from 'cpi_plot.mat' (this assumes you have a similar data structure as in MATLAB)
from scipy.io import loadmat
data = loadmat('cpi_plot.mat')

# Extracting relevant data from the MATLAB struct
cpiinflation = data['cpiinflation']
t = cpiinflation['t'][0][0].flatten()
IT = cpiinflation['IT'][0][0].flatten()
ITup = cpiinflation['ITup'][0][0].flatten()
ITlo = cpiinflation['ITlo'][0][0].flatten()
realized = cpiinflation['realized'][0][0].flatten()

# Prepare xfill and yfill for shaded region
xfill = np.concatenate((t, t[::-1]))
yfill = np.concatenate((ITup, ITlo[::-1]))

# --- First Plot ---
plt.figure(figsize=(10, 5))
fill_color = [0.9, 0.9, 0.9]
plt.fill(xfill, yfill, color=fill_color, label='Target range')

plt.plot(t, IT, 'k:', label='Target point')
plt.plot(t, realized, 'r-o', label='Actual inflation rate')

# Example: Add more series (adjust based on your data structure)
for i in range(3, 10):  # Adjust indices based on available variables
    plt.plot(t, cpiinflation[f'VarName{i}'][0][0].flatten(), label=f'VarName{i}')

# Adjust limits and labels
plt.xlim([2012, 2026])
plt.ylim([0, 6])
plt.xticks(range(2012, 2027))
plt.title('CPI Inflation Rate')
plt.legend(loc='northwest')
plt.show()

# --- Second Plot ---
plt.figure(figsize=(10, 5))
plt.fill(xfill, yfill, color=fill_color, label='Target range')

core = cpiinflation['core'][0][0].flatten()
cpi = cpiinflation['cpi'][0][0].flatten()

plt.plot(t, core, 'b-.', label='Core Inflation')
plt.plot(t, cpi, 'r', label='CPI Inflation')
plt.plot(t, IT, 'k--', label='Target point')

# Adjust limits and labels
plt.xlim([1999, 2025])
plt.ylim([0, 6])
plt.title('Inflation Targets in Korea')
plt.legend(loc='northwest')
plt.show()
