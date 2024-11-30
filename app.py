import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Streamlit File Uploader
st.title("CPI Inflation Visualization")
uploaded_file = st.file_uploader("Upload your CPI Inflation CSV", type=["csv"])
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)

# Load the data
csv_file_path = './cpi_inflation.csv'  # Replace with your local path or use file uploader
data = pd.read_csv(csv_file_path)

# Extract key columns
t = data['t']
realized = data['realized']

# Dummy data for IT, ITup, and ITlo (replace with actual columns if available)
IT = np.linspace(2, 2, len(t))  # Replace with `data['IT']` if present
d = data['t'] < 2016
IT = d*3+(1-d)*2
IT[3:4]=2.5
d1 = data['t'] < 2013
ITup = IT + 0.5*d+0.5*d1
ITlo = IT - 0.5*d-0.5*d1



# Create xfill and yfill for shaded region
xfill = np.concatenate([t, t[::-1]])
yfill = np.concatenate([ITup, ITlo[::-1]])

# Define MATLAB-like color and line style mappings
color_styles = [
    ('b', '--', 'x'),  # blue dashed with 'x' marker
    ('c', '-.', '^'),  # cyan dash-dot with '^' marker
]
dynamic_styles = [color_styles[i % len(color_styles)] for i in range(len(data.columns) - 2)]

# Identify dynamic columns (all except `t` and `realized`)
dynamic_columns = [col for col in data.columns if col not in ['period','t', 'realized']]

# Function to create the plot
@st.cache_data
def create_plot():
    plt.figure(figsize=(10, 5))
    fill_color = [0.9, 0.9, 0.9]
    plt.fill(xfill, yfill, color=fill_color, label='Target range')

    plt.plot(t, IT, 'k:', label='Target point')
    plt.plot(t, realized, 'r-o', label='Actual inflation rate')

    # Add dynamic columns with MATLAB-like styles
    for i, col in enumerate(dynamic_columns):
        color, linestyle, marker = dynamic_styles[i]
        if data[col].notnull().any():
            plt.plot(t, data[col], linestyle=linestyle, color=color, marker=marker, label=col)

    # Configure plot limits and labels
    plt.xlim([2022, 2026])
    plt.ylim([0, 6])
    plt.xticks(range(2022, 2027))
    plt.yticks(range(0,7)) 
    plt.legend(['Target range','Target point','Realization','2nd issue','1st issue']) 
    plt.title('CPI Inflation Rate')
    st.pyplot(plt)  # Display plot in Streamlit

# Display the plot if data is loaded
if not data.empty:
    st.write("### CPI Inflation Rate Plot")
    create_plot()

