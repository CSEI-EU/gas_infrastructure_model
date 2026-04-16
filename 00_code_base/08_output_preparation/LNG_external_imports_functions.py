# import packages
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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