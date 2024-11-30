import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# Streamlit File Uploader
st.title("BoK's Inflation Forecast: Visualization")
uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)

# Load the data
csv_file_path = 'cpi_inflation.csv'  # Replace with your local path or use file uploader
data = pd.read_csv(csv_file_path)

# Extract key columns
t = data['t']
realized = data['realized']

# Dummy data for IT, ITup, and ITlo (replace with actual columns if available)
IT = np.linspace(2, 2, len(t))  # Replace with `data['IT']` if present
d = t<2016
IT = d*3+(1-d)*2
IT[2:4]=2.5


# Define MATLAB-like color and line style mappings
color_styles = [
    ('blue', 'dash', "x",'2nd','2nd issue'),  # blue dashed with 'x' marker
    ('cyan', 'dashdot', 'triangle-up', '1st','1st issue'),  # cyan dash-dot with '^' marker
]
dynamic_styles = [color_styles[i % len(color_styles)] for i in range(len(data.columns) - 2)]

# Identify dynamic columns (all except `t` and `realized`)
dynamic_columns = [col for col in data.columns if col not in ['t', 'realized']]

# Function to create the Plotly plot
def create_plot(start:float,end:float,plot_title:str)->None:
    fig = go.Figure()

    # Add lines for various data series
    fig.add_trace(go.Scatter(x=t, y=IT, mode='lines', line=dict(color='black', dash='dot'), name='Target point'))
    fig.add_trace(go.Scatter(x=t, y=realized, mode='lines+markers', marker=dict(color='red', symbol='circle'), name='Actual inflation rate'))

    # Add dynamic columns with MATLAB-like styles
    for i, col in enumerate(dynamic_columns):
        color, linestyle, marker, group, groupname = dynamic_styles[i]
        if data[col].notnull().any():
            fig.add_trace(go.Scatter(x=t, y=data[col], legendgroup=group, name=groupname, mode='lines+markers', line=dict(color=color, dash=linestyle), marker=dict(symbol=marker)))

    # Customize layout
    fig.update_layout(
        title=plot_title,
        xaxis=dict(title='Time', tickvals=np.arange(1999, end+1)),
        yaxis=dict(title='Inflation Rate', showticksuffix='none'),
        showlegend=False
    )
    fig.update_xaxes(range=[start, end])
    # Show the plot
    st.plotly_chart(fig)

# Display the plot if data is loaded
if not data.empty:
    st.write("### CPI Inflation Rate Plot")
    create_plot(1999,2026,'CPI Inflation Rates and Forecasts')
    st.write('### Bias Corrected Forecasts (Lee and Seong, 2024)')
    create_plot(2021,2026,'Bias Corrected Forecasts (Lee and Seong, 2024)')
else:
    st.write('Please upload your csv file with appropriate structure.')