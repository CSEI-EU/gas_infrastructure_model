# import packages
import pandas as pd
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from output_visualization_functions import *


# To identify if the terminals have increase their capacity or if they are completely new
def identify_terminal_status(df_ports, year):
    df_ports = df_ports.copy()

    # All terminals across all years
    location_years = df_ports.groupby(['Latitude', 'Longitude'])['Model Year'].unique().reset_index()

    # See which were already existing before
    def classify(row):
        years = row['Model Year']
        if year in years and any(y < year for y in years):
            return 'upgraded'
        elif year in years and all(y >= year for y in years):
            return 'new'
        else:
            return 'old'

    location_years['Status'] = location_years.apply(classify, axis=1)

    # Get the status for each row
    df_ports = df_ports.merge(location_years[['Latitude', 'Longitude', 'Status']], on=['Latitude', 'Longitude'], how='left')
    df_ports.loc[df_ports['Model Year'] < year, 'Status'] = 'old'

    return df_ports


# -----------------------------------------------------------------------------------------
# Processing of pipelines excluded for 2024 scenarios 
def build_edges(df):
    return set(df.apply(lambda row: f"{row['Source'].strip()}, {row['Destination'].strip()}", axis=1))

def scenario_pipeline_exclusions(input_excluded_pipelines, pipeline_edges):
    excluded_all = build_edges(pd.read_excel(input_excluded_pipelines, sheet_name='2024'))
    excluded_wRU = build_edges(pd.read_excel(input_excluded_pipelines, sheet_name='2024_wRU'))
    excluded_NOR = build_edges(pd.read_excel(input_excluded_pipelines, sheet_name='2024_NOR'))

    pipeline_status = {}

    for edge in pipeline_edges:
        edge_clean = edge.replace("'", "").strip() if isinstance(edge, str) else str(edge).strip()
        in_all = edge_clean in excluded_all
        in_wRU = edge_clean in excluded_wRU
        in_NOR = edge_clean in excluded_NOR

        if in_all and not in_wRU:
            pipeline_status[edge] = 'included_in_wRU_only'
        elif in_all:
            pipeline_status[edge] = 'excluded_for_all'
        elif in_NOR:
            pipeline_status[edge] = 'excluded_for_NOR_only'
        else:
            pipeline_status[edge] = 'included'

    return pipeline_status



def scenario_pipeline_exclusions_RU(input_excluded_pipelines, pipeline_edges):
    excluded_all = build_edges(pd.read_excel(input_excluded_pipelines, sheet_name='2035'))

    pipeline_status = {}

    for edge in pipeline_edges:
        edge_clean = edge.replace("'", "").strip() if isinstance(edge, str) else str(edge).strip()
        in_all = edge_clean in excluded_all

        if in_all:
            pipeline_status[edge] = 'excluded_for_all'
        else:
            pipeline_status[edge] = 'included'

    return pipeline_status
# -----------------------------------------------------------------------------------------

# Plot the map according to each scenario year 
def plot_map(df_ports, pipelines_df, pipeline_status, year, base_path, save):
    output_path = os.path.join(base_path, "02_plots", f"base_map_{year}.png")
    fig = go.Figure()

    # LNG Terminals
    color_map_ports = {'old': 'black', 'upgraded': 'blue', 'new': 'green'}
    for status in ['old', 'upgraded', 'new']:
        ports = df_ports[df_ports['Status'] == status]
        fig.add_trace(go.Scattergeo(
            lon=ports['Longitude'],
            lat=ports['Latitude'],
            mode='markers',
            marker=dict(size=6, color=color_map_ports[status], symbol='circle'),
            name=f'LNG Terminal ({status})'
        ))

    # Pipelines
    color_map = {
        'included': 'gray',
        'excluded_for_all': 'red',
        'excluded_for_NOR_only': 'purple',
        'included_in_wRU_only': 'red',
    }

    status_name_map = {
        'included': 'Included',
        'excluded_for_all': 'Excluded in all',
        'excluded_for_NOR_only': 'Excluded in Norway scenario only',
        'included_in_wRU_only': 'Included only in Russia scenario',
    }

    legend_shown = set()
    for _, row in pipelines_df.iterrows():
        edge = row['Edge']
        status = pipeline_status.get(edge, 'included')
        color = color_map.get(status, 'gray')

        show_legend = status not in legend_shown
        legend_shown.add(status)

        line_style = dict(width=2, color=color)
        if status == 'included_in_wRU_only':
            line_style['dash'] = 'dot'

        fig.add_trace(go.Scattergeo(
            lon=[row['Source_lon'], row['Target_lon']],
            lat=[row['Source_lat'], row['Target_lat']],
            mode='lines',
            line=line_style,
            name=status_name_map.get(status, 'Included'),
            showlegend=show_legend
        ))

    fig.update_layout(
        geo=dict(
            scope='world',
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(220, 230, 250)',
            showcountries=True,
            countrycolor='rgb(180, 200, 230)',
            showcoastlines=True,
            coastlinecolor='rgb(160, 180, 220)',
            center=dict(lat=50, lon=20),
            lataxis=dict(range=[30, 65]),
            lonaxis=dict(range=[-20, 40]),
        ),
        width=900,
        height=650,
    )

    if save:
        fig.write_image(output_path, width=1135, height=800, scale=2)
    else:
        fig.show()

    return fig


# Updated function for three subplots 
def plot_three_years_subplots(df_ports_2021, pipelines_2021, pipeline_status_2021,df_ports_2024, pipelines_2024, pipeline_status_2024,df_ports_2035, pipelines_2035, pipeline_status_2035,base_path, save=False):
    
    fig = make_subplots(rows=1, cols=3,specs=[[{"type": "scattergeo"}, {"type": "scattergeo"}, {"type": "scattergeo"}]],subplot_titles=("Reference Scenario", "Realized Expansion and Alternative Resilience Scenario", "Planned LNG Expansion Scenario"))
    
    color_map_ports = {'old': 'black', 'upgraded': 'blue', 'new': 'green'}
    color_map_pipelines = {
        'included': 'gray',
        'excluded_for_all': 'red',
        'excluded_for_NOR_only': 'purple',
        'included_in_wRU_only': 'red',
    }
    status_name_map = {
        'included': 'Included',
        'excluded_for_all': 'Excluded in all',
        'excluded_for_NOR_only': 'Disruption from Norway',
        'included_in_wRU_only': 'Only via TurkStream',
    }

    def add_traces(df_ports, pipelines_df, pipeline_status, col, show_legend_ports=False, show_legend_pipes=False):
        # LNG terminals
        for status in ['old', 'upgraded', 'new']:
            ports = df_ports[df_ports['Status'] == status]
            fig.add_trace(go.Scattergeo(
                lon=ports['Longitude'],
                lat=ports['Latitude'],
                mode='markers',
                marker=dict(size=6, color=color_map_ports[status], symbol='circle'),
                name=f'LNG Terminal ({status})',
                showlegend=show_legend_ports
            ), row=1, col=col)
        
        # Pipelines
        legend_shown = set()
        for _, row in pipelines_df.iterrows():
            edge = row['Edge']
            status = pipeline_status.get(edge, 'included')
            color = color_map_pipelines.get(status, 'gray')

            show_legend = status not in legend_shown if show_legend_pipes else False
            legend_shown.add(status)

            line_style = dict(width=2, color=color)
            if status == 'included_in_wRU_only':
                line_style['dash'] = 'dot'

            fig.add_trace(go.Scattergeo(
                lon=[row['Source_lon'], row['Target_lon']],
                lat=[row['Source_lat'], row['Target_lat']],
                mode='lines',
                line=line_style,
                name=status_name_map.get(status, 'Included'),
                showlegend=show_legend
            ), row=1, col=col)

    # Add each year subplot
    add_traces(df_ports_2021, pipelines_2021, pipeline_status_2021, col=1,show_legend_ports=False, show_legend_pipes=False)
    add_traces(df_ports_2024, pipelines_2024, pipeline_status_2024, col=2,show_legend_ports=True, show_legend_pipes=True)  
    add_traces(df_ports_2035, pipelines_2035, pipeline_status_2035, col=3,show_legend_ports=False, show_legend_pipes=False)
    
    # Update layout for all subplots
    for i in range(1, 4):
        fig.update_layout(**{f'geo{i}' if i>1 else 'geo': dict(
        scope='europe',
        projection_type='natural earth',
        showland=True,
        landcolor='rgb(220, 230, 250)',
        showcountries=True,
        countrycolor='rgb(180, 200, 230)',
        showcoastlines=True,
        coastlinecolor='rgb(160, 180, 220)',
        center=dict(lat=50, lon=20),
        lataxis=dict(range=[30, 65]),
        lonaxis=dict(range=[-20, 40]),
    )})
        
    # Update the legend position
    fig.update_layout(
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0,
            xanchor='center',
            x=0.5,
            title=None
        ),
        width=1600,
        height=600,
    )

    if save:
        output_path = os.path.join(base_path, "02_plots", "base_map_3years.png")
        fig.write_image(output_path, width=1000, height=400, scale=3)
    else:
        fig.show()

    return fig


def plot_three_years_2x2(df_ports_2021, pipelines_2021, pipeline_status_2021,
                         df_ports_2024, pipelines_2024, pipeline_status_2024,
                         df_ports_2035, pipelines_2035, pipeline_status_2035,
                         base_path, save=False):
    """
    2x2 layout:
    - Top row: 2021, 2024
    - Bottom row: 2035, Legend (symbols + lines)
    Legend drawn without title, with white background and correct colors/styles.
    """

    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "scattergeo"}, {"type": "scattergeo"}],
               [{"type": "scattergeo"}, {"type": "xy"}]],
        subplot_titles=("Reference Scenario",
                        "Realized Expension & Alternative Resilience Scenario",
                        "Planned LNG Expansion Scenario", ""),
        column_widths=[0.5, 0.5],
        row_heights=[0.5, 0.5],
        horizontal_spacing=0.03,
        vertical_spacing=0.03
    )

    # --- Colors ---
    color_map_ports = {'old': 'black', 'upgraded': 'blue', 'new': 'green'}
    color_map_pipelines = {
        'included': 'gray',
        'excluded_for_all': 'red',
        'excluded_for_NOR_only': 'purple',
        'included_in_wRU_only': 'red',
    }
    status_name_map = {
        'included': 'Included',
        'excluded_for_all': 'Excluded in all',
        'excluded_for_NOR_only': 'Disruption from Norway',
        'included_in_wRU_only': 'Only via TurkStream',
    }

    # --- Helper function to add traces ---
    def add_traces(df_ports, pipelines_df, pipeline_status, row, col):
        for status in ['old', 'upgraded', 'new']:
            ports = df_ports[df_ports['Status'] == status]
            fig.add_trace(go.Scattergeo(
                lon=ports['Longitude'],
                lat=ports['Latitude'],
                mode='markers',
                marker=dict(size=6, color=color_map_ports[status]),
                showlegend=False
            ), row=row, col=col)

        for _, r in pipelines_df.iterrows():
            edge = r['Edge']
            status = pipeline_status.get(edge, 'included')
            color = color_map_pipelines.get(status, 'gray')
            line_style = dict(width=2, color=color)
            if status == 'included_in_wRU_only':
                line_style['dash'] = 'dot'

            fig.add_trace(go.Scattergeo(
                lon=[r['Source_lon'], r['Target_lon']],
                lat=[r['Source_lat'], r['Target_lat']],
                mode='lines',
                line=line_style,
                showlegend=False
            ), row=row, col=col)

    # --- Add maps ---
    add_traces(df_ports_2021, pipelines_2021, pipeline_status_2021, 1, 1)
    add_traces(df_ports_2024, pipelines_2024, pipeline_status_2024, 1, 2)
    add_traces(df_ports_2035, pipelines_2035, pipeline_status_2035, 2, 1)

    # --- Configure maps ---
    for geo_id in ['geo', 'geo2', 'geo3']:
        fig.update_layout(**{
            geo_id: dict(
                scope='europe',
                projection_type='natural earth',
                showland=True,
                landcolor='rgb(220, 230, 250)',
                showcountries=True,
                countrycolor='rgb(180, 200, 230)',
                showcoastlines=True,
                coastlinecolor='rgb(160, 180, 220)',
                center=dict(lat=50, lon=20),
                lataxis=dict(range=[30, 65]),
                lonaxis=dict(range=[-20, 40]),
            )
        })

    # --- Legend items for bottom-right subplot ---
    # --- Legend items grouped into two columns ---
    terminals = [
        {"type": "marker", "color": "black", "label": "Existing LNG Terminal"},
        {"type": "marker", "color": "blue", "label": "Expanded LNG Terminal"},
        {"type": "marker", "color": "green", "label": "New LNG Terminal"},
    ]

    pipelines = [
        {"type": "line", "color": "gray", "label": "Included", "dash": "solid"},
        {"type": "line", "color": "red", "label": "Excluded in all", "dash": "solid"},
        {"type": "line", "color": "purple", "label": "Norwegian Disruption variation", "dash": "solid"},
        {"type": "line", "color": "red", "label": "Only via TurkStream variation", "dash": "dot"},
    ]

    # Fix the axis ranges for the legend subplot
    fig.update_xaxes(range=[0, 1], row=2, col=2, visible=False, autorange=False)
    fig.update_yaxes(range=[0, 1], row=2, col=2, visible=False, autorange=False)

    # --- Layout configuration ---
    marker_size = 10
    text_size = 14
    line_half = 0.012      # line length
    text_offset = 0.05     # text offset (to the right of symbol/line)
    left_col_center = 0.1
    right_col_center = 0.5

    # Vertically centered positions
    y_start = 0.75
    y_gap = 0.12
    y_positions = [y_start - i * y_gap for i in range(max(len(terminals), len(pipelines)))]

    # --- Helper for adding a legend entry ---
    def add_legend_entry(center_x, y, item):
        if item["type"] == "marker":
            # Symbol
            fig.add_trace(go.Scatter(
                x=[center_x], y=[y],
                mode="markers",
                marker=dict(size=marker_size, color=item["color"]),
                showlegend=False,
                hoverinfo="skip"
            ), row=2, col=2)
        else:
            # Line
            fig.add_trace(go.Scatter(
                x=[center_x - line_half, center_x + line_half], y=[y, y],
                mode="lines",
                line=dict(color=item["color"], width=3, dash=item.get("dash", "solid")),
                showlegend=False,
                hoverinfo="skip"
            ), row=2, col=2)

        # Text slightly to the right (same logic as your original)
        fig.add_trace(go.Scatter(
            x=[center_x + text_offset], y=[y],
            text=[item["label"]],
            mode="text",
            textfont=dict(size=text_size),
            showlegend=False,
            hoverinfo="skip",
            textposition="middle right"
        ), row=2, col=2)

    # --- Add both columns ---
    for item, y in zip(terminals, y_positions[:len(terminals)]):
        add_legend_entry(left_col_center, y, item)

    for item, y in zip(pipelines, y_positions[:len(pipelines)]):
        add_legend_entry(right_col_center, y, item)

    fig.update_xaxes(visible=False, row=2, col=2)
    fig.update_yaxes(visible=False, row=2, col=2)

    # --- Layout adjustments ---
    fig.update_layout(
        paper_bgcolor='white',   # entire figure background
        plot_bgcolor='white',    # area behind subplots
        width=1400,
        height=1000
    )

    # --- Save or show ---
    if save:
        output_path = os.path.join(base_path, "02_plots", "base_map_2x2.png")
        fig.write_image(output_path, width=1400, height=1000, scale=3)
    else:
        fig.show()

    return fig