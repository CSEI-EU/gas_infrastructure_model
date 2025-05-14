# import packages
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import sample_colorscale, diverging

import pycountry
from geopy.geocoders import Nominatim
import time



# Compare two years to see new ports added
def get_new_ports(df, year_start, year_end):
    return df[(df['year_added'] > year_start) & (df['year_added'] <= year_end)]


# Plot different colors for ports 
def plot_ports_by_year(df, year_1, year_2, year_3, title):
    fig = go.Figure()

    # Filter the ports by the years
    ports_2021 = df[df['Model Year'] <= year_1]
    ports_2024 = df[(df['Model Year'] > year_1) & (df['Model Year'] <= year_2)]
    ports_2035 = df[df['Model Year'] > year_2]

    # Ports for 2021 
    fig.add_trace(go.Scattergeo(
        locationmode='country names',
        lon=ports_2021['Longitude'],
        lat=ports_2021['Latitude'],
        mode='markers',
        marker=dict(
            size=6,
            color='gray',  # Color for 2021 
            symbol='circle',
        ),
        name=f'Ports in {year_1}',
        showlegend=True,
    ))

    # Ports added for 2024 
    fig.add_trace(go.Scattergeo(
        locationmode='country names',
        lon=ports_2024['Longitude'],
        lat=ports_2024['Latitude'],
        mode='markers',
        marker=dict(
            size=6,
            color='blue',  # Color for 2024 
            symbol='circle',
        ),
        name=f'Ports in {year_2}',
        showlegend=True,
    ))

    # Ports added for 2035 
    fig.add_trace(go.Scattergeo(
        locationmode='country names',
        lon=ports_2035['Longitude'],
        lat=ports_2035['Latitude'],
        mode='markers',
        marker=dict(
            size=6,
            color='green',  # Color for 2035 
            symbol='circle',
        ),
        name=f'Ports in {year_3}',
        showlegend=True,
    ))

    # Update  layout
    fig.update_layout(
        title=title,
        geo=dict(
            scope='world',  # full world, but we control view
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(220, 230, 250)',
            showcountries=True,                 # Shows borders even internal
            countrycolor='rgb(180, 200, 230)',
            showcoastlines=True,
            coastlinecolor='rgb(160, 180, 220)',

            center=dict(lat=50, lon=20),  # Europe-focused
            lataxis=dict(range=[30, 65]),  # N Africa to N Europe
            lonaxis=dict(range=[-20, 40]), # W Europe to Central Asia
        ),
        width=900,
        height=650,
    )

    fig.show()