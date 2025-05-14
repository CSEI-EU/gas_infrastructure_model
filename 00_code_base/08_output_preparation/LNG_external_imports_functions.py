# import packages
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Pie chart of LNG sources for Leurope
def plot_pie_charts(df1, column1, year1, df2, column2, year2, country_map):
    grouped1 = df1.groupby('Region')[column1]
    grouped1.index = grouped1.index.map(lambda x: country_map.get(x, x))
    grouped2 = df2.groupby('Region')[column2]
    grouped2.index = grouped2.index.map(lambda x: country_map.get(x, x))   

    fig, axs = plt.subplots(1, 2, figsize=(14, 7))

    axs[0].pie(grouped1, labels=grouped1.index, autopct='%1.1f%%', startangle=90)
    axs[0].set_title(f"European LNG import sources ({year1})")

    axs[1].pie(grouped2, labels=grouped2.index, autopct='%1.1f%%', startangle=90)
    axs[1].set_title(f"European LNG import sources ({year2})")

    plt.tight_layout()
    plt.show()


# Try and plot with plotly to see difference
def plotly_pie_charts(df1, df2, flow_column, year1, year2):
    # Set dataframe indexes
    grouped1 = df1.set_index('Region')[flow_column]
    grouped2 = df2.set_index('Region')[flow_column]

    # Create pie charts
    fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]],subplot_titles=[str(year1), str(year2)])
    fig.add_trace(go.Pie(labels=grouped1.index, values=grouped1.values, name=str(year1)),row=1, col=1)
    fig.add_trace(go.Pie(labels=grouped2.index, values=grouped2.values, name=str(year2)),row=1, col=2)

    fig.update_layout(
        title_text=f"European LNG import sources: {year1} vs {year2}",
        annotations=[
            dict(text=str(year1), x=0.18, y=0.5, font_size=14, showarrow=False),
            dict(text=str(year2), x=0.82, y=0.5, font_size=14, showarrow=False)
        ]
    )
    fig.show()
