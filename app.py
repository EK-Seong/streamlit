import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import ar1

st.set_page_config(layout="wide")

# Streamlit File Uploader
uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
else:
    # Fallback to local CSV file if none is uploaded
    csv_file_path = 'cpi_inflation.csv'  # Replace with your local path
    data = pd.read_csv(csv_file_path)

# Extract key columns
t = data['t']
realized = data['realized']

# Dummy data for IT, ITup, and ITlo (replace with actual columns if available)
IT = np.linspace(2, 2, len(t))  # Replace with data['IT'] if present
d = t < 2016
IT = d * 3 + (1 - d) * 2
IT[2:4] = 2.5

# Identify dynamic columns (all except t and realized)
dynamic_columns = [col for col in data.columns if col not in ['t', 'realized']]

# Define MATLAB-like color and line style mappings
color_styles = [
    ('blue', 'dash', "x", '2nd', '2nd issue'),  # blue dashed with 'x' marker
    ('cyan', 'dashdot', 'triangle-up', '1st', '1st issue'),  # cyan dash-dot with '^' marker
]

# Repeat color styles if you have more columns than styles
dynamic_styles = [
    color_styles[i % len(color_styles)]
    for i in range(len(dynamic_columns))
]

def create_plot(start: float, end: float):
    """
    Create a Plotly figure showing:
      - The target line (IT)
      - The realized series
    """
    fig = go.Figure()

    # Add lines for various data series
    fig.add_trace(go.Scatter(
        x=t,
        y=IT,
        mode='lines',
        line=dict(color='black', dash='dot'),
        name='Target'
    ))
    fig.add_trace(go.Scatter(
        x=t,
        y=realized,
        mode='lines+markers',
        marker=dict(color='red', symbol='circle'),
        name='Realized'
    ))

    # Customize layout
    fig.update_layout(
        title='CPI Inflation Rates and Forecasts',
        xaxis=dict(title='Time', tickvals=np.arange(1999, end + 1)),
        yaxis=dict(title='Inflation Rate', showticksuffix='none'),
        showlegend=True
    )
    fig.update_xaxes(range=[start, end])

    # Show the plot in Streamlit
    st.plotly_chart(fig)

def bias_correct():
    """
    Combine all selected forecasts and their bias corrections into one graph.
    """
    st.subheader("Select Forecast Columns for Bias Correction")

    # Display checkboxes for the most recent 6 series
    recent_columns = dynamic_columns[-6:] if len(dynamic_columns) >= 6 else dynamic_columns
    columns_to_show = []

    cols = st.columns(len(recent_columns))
    for i, col in enumerate(recent_columns):
        if cols[i].checkbox(f"{col}", value=False):
            columns_to_show.append(col)

    if columns_to_show:
        fig = go.Figure()

        # Add the realized series
        fig.add_trace(go.Scatter(
            x=t,
            y=realized,
            mode='lines+markers',
            marker=dict(color='red', symbol='circle'),
            name='Realized'
        ))

        # Add each selected column and its bias correction
        for col_name in columns_to_show:
            bok = data[col_name]

            # Add the original forecast series
            fig.add_trace(go.Scatter(
                x=t,
                y=bok,
                name=f'Forecast: {col_name}',
                mode='lines+markers',
                line=dict(color='blue', dash='dot'),
                marker=dict(symbol='x')
            ))

            # Compute bias correction
            ehats = ar1.compute_ehats('infl.csv')
            non_nan_indices = bok[bok.notnull()].index.tolist()
            issue_num = 2  # Example value; you can adjust as needed

            if issue_num == 2:
                bc = data[col_name].copy()
                for i in range(0, 3):
                    bc[non_nan_indices[i]] += ehats[2 * i]
            else:
                bc = data[col_name].copy()
                for i in range(0, 2):
                    bc[non_nan_indices[i]] += ehats[2 * i + 1]

            # Add the bias-corrected series
            fig.add_trace(go.Scatter(
                x=t,
                y=bc,
                name=f'Corrected: {col_name}',
                mode='markers',
                marker=dict(color='green', symbol='triangle-up')
            ))

        # Customize layout
        fig.update_layout(
            title='Forecasts and Bias Corrections Combined',
            xaxis=dict(title='Time', tickvals=np.arange(1999, 2027)),
            yaxis=dict(title='Inflation Rate', showticksuffix='none'),
            showlegend=True
        )
        fig.update_xaxes(range=[2022, 2026])

        # Show the plot in Streamlit
        st.plotly_chart(fig)

# Display the plot if data is loaded
if not data.empty:
    st.title("The Real-time Inflation Forecast and Bias Correction")
    st.markdown('[Seojeong Lee](https://sites.google.com/site/misspecifiedjay), [Eunkyu Seong](https://ek-seong.github.io/ekseong/)')

    with open('block1.md', 'r') as file:
        block1 = file.read()
    st.markdown(block1, unsafe_allow_html=True)

    # Create the main figure
    create_plot(1999, 2026)

    with open('block2.md', 'r') as file:
        block2 = file.read()
    st.markdown(block2, unsafe_allow_html=True)

    with open('block3.md', 'r') as file:
        block3 = file.read()
    st.markdown(block3, unsafe_allow_html=True)

    # Bias correction with checkboxes for recent 6 series combined in one graph
    bias_correct()

    st.write('Last Update: Dec 2024')

else:
    st.write('Please upload your CSV file with the appropriate structure.')
