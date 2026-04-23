from logging import config
import os
import geopandas as gpd
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from matplotlib.patches import Patch
import requests
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.lines import Line2D

def clean_world_file(world, ukr_df, fix_iso_dict):
    world = world[world["CONTINENT"] != "Antarctica"] 

    world = world[world["NAME"] != "Ukraine"]  # remove old Ukraine
    ukraine_corrected = ukr_df.rename(columns={"GID_0":"ISO_A3", "NAME_0":"NAME"})
    world = pd.concat([world, ukraine_corrected], ignore_index=True)

    world["ISO_A3"] = world.apply(lambda row: fix_iso_dict.get(row["NAME"], row["ISO_A3"]), axis=1)
    return world



def human_readable(val):
    if val >= 1_000_000:
        return f"{round(val/1_000_000,1)}M"
    elif val >= 1_000:
        return f"{round(val/1_000)}k"
    else:
        return str(int(val))
    

def map_config(data_gas_prod, scenarios):

    vals_for_scaling = data_gas_prod.loc[data_gas_prod['Country'] != "Total", scenarios].values.flatten()
    vals_for_scaling = np.array(vals_for_scaling, dtype=float)

    global_max_raw = vals_for_scaling.max()
    global_max_sqrt = np.sqrt(global_max_raw)

    config = {
        "global_max_raw": global_max_raw,
        "global_max_sqrt": global_max_sqrt,

        "bar_height_scale": 28,
        "bar_spacing": 3,
        "bar_colors": ["#4f81bd", "#2ca02c", "#ca2e2e"],

        "bar_position_fixed": {"North America": (-98.5, 39.8), 
                               "Middle East": (41.50, 27.6)},
        "scale_lon": -150,
        "scale_lat": -50,
        "scale_vals": [0, int(global_max_raw/2), int(global_max_raw)],

        "pastel_colors": {
            "Africa": "#c7e9c0",
            "North America": "#bae4f5",
            "South America": "#7cc2f3",
            "Middle East": "#fdd0a2",
            "Caspian Region": "#fdae6b",
            "Asia": "#fcbba1",
            "Russia": "#fee6ce",
            "Australia": "#dadaeb",
        }
    }

    return config


def build_plotly_map(data_gas_prod, world_df, ports_df, country_points, region_to_countries, highlight_countries, scenarios, config, connectors, output_path, title_plotly, save_output):
    fig = go.Figure()

    for _, row in world_df.iterrows():
        geom = row.geometry
        color = row["fill_color"]
        if geom is None or geom.is_empty:
            continue
        if geom.geom_type == "MultiPolygon":
            for part in geom.geoms:
                lon, lat = list(part.exterior.xy[0]), list(part.exterior.xy[1])
                fig.add_trace(go.Scattergeo(lon=lon, lat=lat, mode="lines", fill="toself", fillcolor=color, line=dict(color="grey", width=0.5), showlegend=False))
        else:
            lon, lat = list(geom.exterior.xy[0]), list(geom.exterior.xy[1])
            fig.add_trace(go.Scattergeo(lon=lon, lat=lat, mode="lines", fill="toself", fillcolor=color, line=dict(color="grey", width=0.5), showlegend=False))
        

    for iso, col in highlight_countries.items():
        g = world_df[world_df["ISO_A3"] == iso]
        if g.empty:
            continue
        for geom in g.geometry:
            if geom.geom_type == "MultiPolygon":
                for part in geom.geoms:
                    lon, lat = list(part.exterior.xy[0]), list(part.exterior.xy[1])
                    fig.add_trace(go.Scattergeo(lon=lon, lat=lat, mode='lines', line=dict(color=col, width=2), showlegend=False))
            else:
                lon, lat = list(geom.exterior.xy[0]), list(geom.exterior.xy[1])
                fig.add_trace(go.Scattergeo(lon=lon, lat=lat, mode='lines', line=dict(color=col, width=2), showlegend=False))

    fig.add_trace(go.Scattergeo(lon=ports_df["Longitude"].tolist(), lat=ports_df["Latitude"].tolist(), mode="markers", marker=dict(size=6, color="black"), name="LNG Ports"))
    
    if connectors:
        europe_hub_lon = -10
        europe_hub_lat = 47

        for country, (lon, lat) in country_points.items():
            fig.add_trace(go.Scattergeo(
            lon=[lon, europe_hub_lon],
            lat=[lat, europe_hub_lat],
            mode="lines",
            line=dict(color="black", width=1.5, dash="dot"),
            opacity=0.6,
            showlegend=False
        ))

        fig.add_trace(go.Scattergeo(lon=[europe_hub_lon], lat=[europe_hub_lat], mode="markers", marker=dict(size=8, color="blue"), name="European LNG demand hub"))
        fig.add_trace(go.Scattergeo(lon=[None], lat=[None], mode="lines", line=dict(color="black", dash="dot", width=1.5), name="Indicative LNG supply routes to Europe"))


    for region_name, isos in region_to_countries.items():
        if region_name not in data_gas_prod['Country'].values:
            continue

        region_geom = world_df[world_df['ISO_A3'].isin(isos)]
        if region_geom.empty:
            continue

        if region_name in config["bar_position_fixed"]:
            x, y = config["bar_position_fixed"][region_name]
        else:
            centroid = region_geom.union_all().centroid
            x, y = centroid.x, centroid.y

        vals = data_gas_prod.loc[data_gas_prod['Country'] == region_name, scenarios].values.flatten()
        vals_scaled = np.sqrt(vals) / config["global_max_sqrt"] * config["bar_height_scale"]

        offsets = np.linspace(-config["bar_spacing"], config["bar_spacing"], len(vals))
        for i, (val, offset) in enumerate(zip(vals_scaled, offsets)):
            fig.add_trace(go.Scattergeo(lon=[x + offset, x + offset], lat=[y, y + val], mode="lines", line=dict(color=config["bar_colors"][i], width=8),
                                        showlegend=(region_name == list(region_to_countries.keys())[0]),
                                        name=({ "2021": "Reference Scenario", "2024": "Realized Expansion and<br>Alternative resilience scenario",
                                        "2035 High Demand": "Planned LNG Expansion<br>Scenario with the Ap and SP variation"}[scenarios[i]] if (region_name == list(region_to_countries.keys())[0])
                                        else None)))



    for val in config["scale_vals"]:
        lat0 = config["scale_lat"]
        lat1 = config["scale_lat"] + (np.sqrt(val) / config["global_max_sqrt"]) * config["bar_height_scale"]

        fig.add_trace(go.Scattergeo(lon=[config["scale_lon"], config["scale_lon"]], lat=[lat0, lat1], mode="lines", line=dict(color="darkgrey", width=8), showlegend=False))
        fig.add_trace(go.Scattergeo(lon=[config["scale_lon"] - 2, config["scale_lon"] + 2], lat=[lat1, lat1], mode="lines", line=dict(color="black", width=2), showlegend=False))
        fig.add_trace(go.Scattergeo(lon=[config["scale_lon"] - 15], lat=[lat1], mode="text",text=[f"{human_readable(val)} GWh/a"], showlegend=False, textfont=dict(size=10)))
        

    for region_name, color in config["pastel_colors"].items():
        label = "Oceania" if region_name == "Australia" else region_name
        fig.add_trace(go.Scattergeo(lon=[None], lat=[None], mode="markers", marker=dict(size=10, color=color, line=dict(width=0.5, color="grey")),showlegend=True,name=label))

    fig.add_trace(go.Scattergeo(lon=[None], lat=[None], mode="lines", line=dict(color="black", width=1), name="National Node (individual Subregion)", showlegend=True))
    
    fig.update_geos(showland=True, landcolor='rgb(220, 230, 250)', showcountries=True, countrycolor='rgb(180, 200, 230)', showcoastlines=True, coastlinecolor='rgb(160, 180, 220)',projection_type='equirectangular')
    fig.update_layout(height=800, width=1130, margin={"r": 0, "t": 0, "l": 0, "b": 0},
                        legend=dict(orientation="h", yanchor="bottom", y=0.16, xanchor="center", x=0.5, font=dict(size=10), itemwidth=30, itemsizing="constant", bordercolor="lightgrey", borderwidth=1))  
    
    fig.show()

    if save_output:
        os.makedirs(output_path, exist_ok=True)
        output_file = os.path.join(output_path, title_plotly)
        fig.write_image(output_file, width=900, height=650, scale=2)