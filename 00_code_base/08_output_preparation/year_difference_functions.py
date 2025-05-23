# import packages
import pandas as pd
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import sample_colorscale, diverging
import pycountry

def scenario_pipeline_exclusions(input_excluded_pipelines, pipeline_edges):
    def build_edges(df):
        return set(df.apply(lambda row: f"{row['Source'].strip()}, {row['Destination'].strip()}", axis=1))

    excluded_all_df = pd.read_excel(input_excluded_pipelines, sheet_name='2024')
    excluded_wRU_df = pd.read_excel(input_excluded_pipelines, sheet_name='2024_wRU')
    excluded_NOR_df = pd.read_excel(input_excluded_pipelines, sheet_name='2024_NOR')

    excluded_all = build_edges(excluded_all_df)
    excluded_wRU = build_edges(excluded_wRU_df)
    excluded_NOR = build_edges(excluded_NOR_df)

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


def plot_baseline(base_path, df_ports, pipelines_df, pipeline_status, year_1, year_2, year_3, save):
    output_file = os.path.join(base_path, "02_plots", f"base_map.png")
    fig = go.Figure()

    # Ports by year groups
    ports_by_year = {
        year_1: df_ports[df_ports['Model Year'] <= year_1],
        year_2: df_ports[(df_ports['Model Year'] > year_1) & (df_ports['Model Year'] <= year_2)],
        year_3: df_ports[df_ports['Model Year'] > year_2]
    }
    colors = {year_1: 'black', year_2: 'blue', year_3: 'green'}

    for year, ports in ports_by_year.items():
        fig.add_trace(go.Scattergeo(
            lon=ports['Longitude'], 
            lat=ports['Latitude'],
            mode='markers',
            marker=dict(size=6, color=colors[year], symbol='circle'),
            name=f'LNG terminal in {year}',
            showlegend=True
        ))

    # For legend tracking to avoid duplicates
    legend_shown = set()
    color_map = {
    'included': 'gray',
    'excluded_for_all': 'red',
    'excluded_for_NOR_only': 'purple',
    'excluded_for_wRU_only': 'orange',
    'included_in_wRU_only': 'red',
    }

    status_name_map = {
    'included': 'Included',
    'excluded_for_all': 'Excluded in all',
    'excluded_for_NOR_only': 'Excluded in Norway scenario only',
    'excluded_for_wRU_only': 'Excluded in Russia scenario only',
    'included_in_wRU_only': 'Included only in Russia scenario',
    }

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
        fig.write_image(output_file, width=1135, height=800, scale=2)
    else:
        fig.show()

    return fig