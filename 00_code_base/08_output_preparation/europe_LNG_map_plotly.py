import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import json
from shapely.geometry import shape
import shapely
from math import cos, radians

save_output = False
scenarios = ["2021", "2024", "2035 High Demand", "2035 Low Demand"]

base_path = r"C:\Users\jfg.eco\Documents\hydrogen_grid"

# Input data
input_file_path = os.path.join(base_path, '01_data', '01_input_data', '02_processed', '01_paper_IAEE', '01_data_sheets_input')
input_file = 'paper_paris_2025_input_production_europe_capacities.xlsx'
full_input_path = os.path.join(input_file_path, input_file)
data_gas_prod = pd.read_excel(full_input_path)

# Fix commas and convert numeric
for col in scenarios:
    data_gas_prod[col] = data_gas_prod[col].astype(str).str.replace(",", ".", regex=False).astype(float)

# Add missing countries
for c in ["Sweden", "Montenegro"]:
    if c not in data_gas_prod["Country"].values:
        data_gas_prod = pd.concat([
            data_gas_prod,
            pd.DataFrame([{"Country": c, **{s: 0.0 for s in scenarios}}])
        ], ignore_index=True)

# Exclude Total row for plot and calculations
excel_countries = data_gas_prod[data_gas_prod["Country"] != "Total"].copy()

# Output path
output_path = "02_plots"

# Country ISO3 mapping
country_name_to_iso3 = {
    "Albania": "ALB", "Austria": "AUT", "Belarus": "BLR", "Belgium": "BEL",
    "Bosnia and Herzegovina": "BIH", "Bulgaria": "BGR", "Croatia": "HRV",
    "Czech Republic": "CZE", "Denmark": "DNK", "Estonia": "EST", "Finland": "FIN",
    "France": "FRA", "Germany": "DEU", "Greece": "GRC", "Hungary": "HUN",
    "Ireland": "IRL", "Italy": "ITA", "Latvia": "LVA", "Lithuania": "LTU",
    "Luxemburg": "LUX", "Moldova": "MDA", "Netherlands": "NLD",
    "North Macedonia": "MKD", "Norway": "NOR", "Poland": "POL",
    "Portugal": "PRT", "Romania": "ROU", "Serbia": "SRB", "Slovakia": "SVK",
    "Slovenia": "SVN", "Spain": "ESP", "Switzerland": "CHE", "Türkiye": "TUR",
    "UK": "GBR", "Ukraine": "UKR", "Kosovo": "XKX", "Sweden": "SWE",
    "Montenegro": "MNE", "Malta": "MLT"
}
excel_countries["ISO_A3"] = excel_countries["Country"].map(country_name_to_iso3)

# Country colors (Producing vs Non-Producing)
pastel_colors = {"Producing": "#a1a0a0", "Non-Producing": "#dddddd"}
def country_color(row):
    vals = row[scenarios].values
    return pastel_colors["Producing"] if np.any(vals > 0) else pastel_colors["Non-Producing"]

excel_countries["color"] = excel_countries.apply(country_color, axis=1)

# Bar scaling setup
vals_for_scaling = excel_countries[scenarios].values.flatten()
global_max_raw = np.max(vals_for_scaling)
global_max_sqrt = np.sqrt(global_max_raw)
bar_height_scale = 7
bar_colors = ["#4f81bd", "#2ca02c", "#ca2e2e", "#732ca0"]
bar_spacing = 0.7
bar_position_fixed = {
    "Slovakia": (0.6, 0),
    "Hungary": (-0.6, 0),
    "Norway": (2, 0),
    "Germany": (1, 0)
}

# Country coordinates
COUNTRY_COORDINATES = {
    'ALB': (20.1683, 41.1533), 'AUT': (14.5501, 47.5162), 'BLR': (27.9534, 53.7098),
    'BEL': (4.3517, 50.8503), 'BIH': (17.6791, 43.9159), 'BGR': (25.4858, 42.7339),
    'HRV': (15.2, 45.1), 'CZE': (15.4730, 49.8175), 'DNK': (9.5018, 56.2639),
    'EST': (25.0136, 58.5953), 'FIN': (25.7482, 61.9241), 'FRA': (1.8883, 46.6034),
    'DEU': (10.4515, 51.1657), 'GRC': (21.8243, 39.0742), 'HUN': (19.5033, 47.1625),
    'IRL': (-7.6921, 53.1424), 'ITA': (12.5674, 41.8719), 'LVA': (24.6032, 56.8796),
    'LTU': (23.8813, 55.1694), 'LUX': (6.1296, 49.8153), 'MDA': (28.3699, 47.4116),
    'NLD': (5.2913, 52.1326), 'MKD': (21.4254, 41.9981), 'NOR': (6.7, 60.4720),
    'POL': (19.1451, 51.9194), 'PRT': (-8.2245, 39.3999), 'ROU': (24.9668, 45.9432),
    'SRB': (21.0059, 44.0165), 'SVK': (19.6990, 48.6690), 'SVN': (14.9955, 46.1512),
    'ESP': (-3.7492, 40.4637), 'CHE': (8.2275, 46.8182), 'TUR': (35.0, 39.0),
    'GBR': (-1.5, 51.0), 'UKR': (31.1656, 48.3794), 'XKX': (20.9020, 42.6026),
    'SWE': (14.5, 58), 'MNE': (19.3744, 42.7087), 'MLT': (14.3754, 35.9375)
}

def get_country_coordinates(iso3):
    return COUNTRY_COORDINATES.get(iso3, (10, 50))

# Load Ukraine GeoJSON (Crimea fix)
ukraine_json_url = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_UKR_0.json"
ukraine_json_path = os.path.join(base_path, "00_code_base", "08_output_preparation", "gadm41_UKR_0.json")
if not os.path.exists(ukraine_json_path):
    os.makedirs(os.path.dirname(ukraine_json_path), exist_ok=True)
    with open(ukraine_json_path, "wb") as f:
        f.write(requests.get(ukraine_json_url).content)
with open(ukraine_json_path, "r", encoding="utf-8") as f:
    ukraine_geojson = json.load(f)

def get_centroid_from_geojson(geojson_feature):
    geom = shape(geojson_feature["geometry"])
    if isinstance(geom, shapely.geometry.multipolygon.MultiPolygon):
        largest = max(geom.geoms, key=lambda p: p.area)
        return largest.centroid
    else:
        return geom.centroid

# Create figure
fig = go.Figure()

# Add base layer: non-producing countries
non_prod_countries = excel_countries[excel_countries["color"] == pastel_colors["Non-Producing"]]
fig.add_trace(go.Choropleth(
    locations=non_prod_countries["ISO_A3"],
    z=[0]*len(non_prod_countries),
    colorscale=[[0, pastel_colors["Non-Producing"]], [1, pastel_colors["Non-Producing"]]],
    showscale=False,
    marker_line_color='white',
    marker_line_width=0.5,
    name="Not producing",
    showlegend=True
))

# Add producing countries (gray)
prod_countries = excel_countries[excel_countries["color"] == pastel_colors["Producing"]]
fig.add_trace(go.Choropleth(
    locations=prod_countries["ISO_A3"],
    z=[0]*len(prod_countries),
    colorscale=[[0, pastel_colors["Producing"]], [1, pastel_colors["Producing"]]],
    showscale=False,
    marker_line_color='white',
    marker_line_width=0.5,
    name="Producing European country",
    showlegend=True
))

# Ukraine separately
ukr_row = excel_countries[excel_countries["ISO_A3"]=="UKR"]
if not ukr_row.empty:
    color_type = "Producing" if (ukr_row[scenarios].values > 0).any() else "Non-Producing"
    fig.add_trace(go.Choropleth(
        geojson=ukraine_geojson,
        featureidkey="properties.GID_0",
        locations=ukr_row["ISO_A3"],
        z=[0],
        colorscale=[[0, pastel_colors[color_type]], [1, pastel_colors[color_type]]],
        showscale=False,
        marker_line_color='white',
        marker_line_width=0.5,
        name="Ukraine",
        showlegend=False
    ))

# Bar plots
scenario_labels = [
    "Reference Scenario",
    "Realized Expansion and<br>Alternative resilience scenario",
    "Planned LNG Expansion<br>Scenario (Stated Policies)",
    "Planned LNG Expansion<br>Scenario (Announced Policies)"
]

for idx, row in excel_countries.iterrows():
    iso3 = row["ISO_A3"]
    vals = np.array(row[scenarios], dtype=float)
    vals = np.nan_to_num(vals, nan=0.0)
    vals_scaled = np.sqrt(vals) / global_max_sqrt * bar_height_scale

    if iso3 == "UKR":
        centroid = get_centroid_from_geojson(ukraine_geojson["features"][0])
        x, y = centroid.x, centroid.y
    else:
        lon, lat = get_country_coordinates(iso3)
        x, y = lon, lat

    if row["Country"] in bar_position_fixed:
        x += bar_position_fixed[row["Country"]][0]
        y += bar_position_fixed[row["Country"]][1]

    offsets = np.linspace(-bar_spacing, bar_spacing, len(vals))
    for i, (val, offset) in enumerate(zip(vals_scaled, offsets)):
        fig.add_trace(go.Scattergeo(
            lon=[x+offset, x+offset],
            lat=[y, y+val],
            mode="lines",
            line=dict(color=bar_colors[i], width=6),
            name=scenario_labels[i] if idx==0 else None,
            showlegend=(idx==0)
        ))

# Layout and legend
fig.update_geos(
    scope='world',
    projection_type='natural earth',
    showland=True,
    landcolor='rgb(240, 245, 255)',
    showcountries=True,
    countrycolor='rgb(180, 200, 230)',
    showcoastlines=True,
    coastlinecolor='rgb(160, 180, 220)',
    center=dict(lat=50, lon=20),
    lataxis=dict(range=[30, 65]),
    lonaxis=dict(range=[-25, 40]),
)

fig.update_layout(
        geo=dict(
            scope='world',  # or 'world'
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(220, 230, 250)',
            showcountries=True,
            countrycolor='rgb(180, 200, 230)',
            showcoastlines=True,
            coastlinecolor='rgb(160, 180, 220)',
            center=dict(lat=50, lon=20),
            lataxis=dict(range=[30, 65]),
            lonaxis=dict(range=[-25, 40]),
        ),
        legend=dict(
            x=0.965,  
            y=0.92,
            xanchor='right',
            yanchor='top',
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(0, 0, 0, 0.8)',
            borderwidth=1,
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        width=900,
        height=650
    )

def human_readable(val):
    absolute_val = val * global_max_raw  
    if absolute_val >= 1_000_000:
        return f"{round(absolute_val/1_000_000,1)}M"
    elif absolute_val >= 1_000:
        return f"{round(absolute_val/1_000)}k"
    else:
        return str(int(absolute_val))
    
# Base coordinates for the legend
scale_lon, scale_lat = 45, 48  # adjust as needed
legend_bar_width = 8
legend_label_offset_lon = 3  # distance of label from bar

# Fractions of the maximum for intermediate bars
scale_vals = [0.25, 0.5, 0.75, 1.0]

for val_frac in scale_vals:
    val_height = np.sqrt(val_frac * global_max_raw) / global_max_sqrt * bar_height_scale
    
    # Draw vertical bar 
    fig.add_trace(go.Scattergeo(
        lon=[scale_lon, scale_lon + 0.3],
        lat=[scale_lat, scale_lat + val_height],
        mode="lines",
        line=dict(color="darkgrey", width=legend_bar_width),
        showlegend=False
    ))
    
    # Draw the label 
    fig.add_trace(go.Scattergeo(
        lon=[scale_lon - legend_label_offset_lon],
        lat=[scale_lat + val_height],
        mode="text",
        text=[f"{human_readable(val_frac)} GWh/a"],
        showlegend=False,
        textfont=dict(size=10, color="black"),
        hoverinfo='skip'
    ))

# Show or save
if save_output:
    os.makedirs(output_path, exist_ok=True)
    fig.write_image(os.path.join(output_path, "europe_bar_plot_simple.png"), width=900, height=600, scale=2)
else:
    fig.show()


# ALTERNATIVE

import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import json
from shapely.geometry import shape
import shapely

save_output = False
scenarios = ["2021", "2024", "2035 High Demand", "2035 Low Demand"]

base_path = r"C:\Users\jfg.eco\Documents\hydrogen_grid"

# ---------- LOAD INPUT DATA ----------
input_file_path = os.path.join(base_path, '01_data', '01_input_data', '02_processed', '01_paper_IAEE', '01_data_sheets_input')
input_file = 'paper_paris_2025_input_production_europe_capacities.xlsx'
full_input_path = os.path.join(input_file_path, input_file)
data_gas_prod = pd.read_excel(full_input_path)

# Fix commas and convert numeric
for col in scenarios:
    data_gas_prod[col] = data_gas_prod[col].astype(str).str.replace(",", ".", regex=False).astype(float)

# Add missing countries
for c in ["Sweden", "Montenegro"]:
    if c not in data_gas_prod["Country"].values:
        data_gas_prod = pd.concat([
            data_gas_prod,
            pd.DataFrame([{"Country": c, **{s: 0.0 for s in scenarios}}])
        ], ignore_index=True)

# Exclude Total row
excel_countries = data_gas_prod[data_gas_prod["Country"] != "Total"].copy()

# Output path
output_path = "02_plots"

# ---------- COUNTRY ISO3 MAPPING ----------
country_name_to_iso3 = {
    "Albania": "ALB", "Austria": "AUT", "Belarus": "BLR", "Belgium": "BEL",
    "Bosnia and Herzegovina": "BIH", "Bulgaria": "BGR", "Croatia": "HRV",
    "Czech Republic": "CZE", "Denmark": "DNK", "Estonia": "EST", "Finland": "FIN",
    "France": "FRA", "Germany": "DEU", "Greece": "GRC", "Hungary": "HUN",
    "Ireland": "IRL", "Italy": "ITA", "Latvia": "LVA", "Lithuania": "LTU",
    "Luxemburg": "LUX", "Moldova": "MDA", "Netherlands": "NLD",
    "North Macedonia": "MKD", "Norway": "NOR", "Poland": "POL",
    "Portugal": "PRT", "Romania": "ROU", "Serbia": "SRB", "Slovakia": "SVK",
    "Slovenia": "SVN", "Spain": "ESP", "Switzerland": "CHE", "Türkiye": "TUR",
    "UK": "GBR", "Ukraine": "UKR", "Kosovo": "XKX", "Sweden": "SWE",
    "Montenegro": "MNE", "Malta": "MLT"
}
excel_countries["ISO_A3"] = excel_countries["Country"].map(country_name_to_iso3)

# ---------- COLORS ----------
pastel_colors = {"Producing": "#a1a0a0", "Non-Producing": "#dddddd"}
def country_color(row):
    vals = row[scenarios].values
    return pastel_colors["Producing"] if np.any(vals > 0) else pastel_colors["Non-Producing"]
excel_countries["color"] = excel_countries.apply(country_color, axis=1)

# ---------- BAR SCALING ----------
vals_for_scaling = excel_countries[scenarios].values.flatten()
global_max_raw = np.max(vals_for_scaling)
global_max_sqrt = np.sqrt(global_max_raw)
bar_height_scale = 7
bar_colors = ["#4f81bd", "#2ca02c", "#ca2e2e", "#732ca0"]
bar_spacing = 0.7
bar_position_fixed = {
    "Slovakia": (0.6, 0),
    "Hungary": (-0.6, 0),
    "Norway": (2, 0),
    "Germany": (1, 0)
}

# ---------- COUNTRY COORDINATES ----------
COUNTRY_COORDINATES = {
    'ALB': (20.1683, 41.1533), 'AUT': (14.5501, 47.5162), 'BLR': (27.9534, 53.7098),
    'BEL': (4.3517, 50.8503), 'BIH': (17.6791, 43.9159), 'BGR': (25.4858, 42.7339),
    'HRV': (15.2, 45.1), 'CZE': (15.4730, 49.8175), 'DNK': (9.5018, 56.2639),
    'EST': (25.0136, 58.5953), 'FIN': (25.7482, 61.9241), 'FRA': (1.8883, 46.6034),
    'DEU': (10.4515, 51.1657), 'GRC': (21.8243, 39.0742), 'HUN': (19.5033, 47.1625),
    'IRL': (-7.6921, 53.1424), 'ITA': (12.5674, 41.8719), 'LVA': (24.6032, 56.8796),
    'LTU': (23.8813, 55.1694), 'LUX': (6.1296, 49.8153), 'MDA': (28.3699, 47.4116),
    'NLD': (5.2913, 52.1326), 'MKD': (21.4254, 41.9981), 'NOR': (6.7, 60.4720),
    'POL': (19.1451, 51.9194), 'PRT': (-8.2245, 39.3999), 'ROU': (24.9668, 45.9432),
    'SRB': (21.0059, 44.0165), 'SVK': (19.6990, 48.6690), 'SVN': (14.9955, 46.1512),
    'ESP': (-3.7492, 40.4637), 'CHE': (8.2275, 46.8182), 'TUR': (35.0, 39.0),
    'GBR': (-1.5, 51.0), 'UKR': (31.1656, 48.3794), 'XKX': (20.9020, 42.6026),
    'SWE': (14.5, 58), 'MNE': (19.3744, 42.7087), 'MLT': (14.3754, 35.9375)
}
def get_country_coordinates(iso3):
    return COUNTRY_COORDINATES.get(iso3, (10, 50))

# ---------- CREATE BASE MAP FIGURE ----------
fig_map = go.Figure()

fig_map = go.Figure()

for idx, row in excel_countries.iterrows():
    lon, lat = get_country_coordinates(row["ISO_A3"])
    # Draw a simple square for the country as placeholder
    width, height = 2, 2
    fig_map.add_trace(go.Scatter(
        x=[lon-width/2, lon-width/2, lon+width/2, lon+width/2, lon-width/2],
        y=[lat-height/2, lat+height/2, lat+height/2, lat-height/2, lat-height/2],
        fill="toself",
        fillcolor=row["color"],
        line=dict(color="white"),
        name=row["Country"],
        showlegend=False
    ))

fig_map.update_xaxes(range=[-10, 20])
fig_map.update_yaxes(range=[35, 55])
fig_map.update_layout(
    width=900, height=650,
    title="Europe Map (Standalone)",
    margin=dict(l=0,r=0,t=40,b=0)
)

# Show the map
fig_map.show()

# Save base map as image
if save_output:
    os.makedirs(output_path, exist_ok=True)
    map_file = os.path.join(output_path, "map_background.png")
else:
    map_file = "map_background.png"
fig_map.update_layout(
    xaxis=dict(range=[-25, 40], visible=False),
    yaxis=dict(range=[30, 65], visible=False),
    width=900,
    height=650,
    margin=dict(l=0,r=0,t=0,b=0)
)
fig_map.write_image(map_file)

# ---------- CREATE FINAL FIGURE WITH MAP BACKGROUND ----------
fig = go.Figure()

# Add map as background image
fig.add_layout_image(
    dict(
        source="europe_map.png",
        xref="x",
        yref="y",
        x=-25,            # left edge of your data x-axis
        y=65,             # top edge of your data y-axis
        sizex=65,         # width: x_max - x_min
        sizey=35,         # height: y_max - y_min
        xanchor="left",
        yanchor="top",
        sizing="stretch",
        layer="below"
    )
)

# Add bars
scenario_labels = [
    "Reference Scenario",
    "Realized Expansion and Alternative resilience scenario",
    "Planned LNG Expansion Scenario (Stated Policies)",
    "Planned LNG Expansion Scenario (Announced Policies)"
]

for idx, row in excel_countries.iterrows():
    iso3 = row["ISO_A3"]
    vals = np.array(row[scenarios], dtype=float)
    vals = np.nan_to_num(vals, nan=0.0)
    vals_scaled = np.sqrt(vals) / global_max_sqrt * bar_height_scale

    lon, lat = get_country_coordinates(iso3)
    if row["Country"] in bar_position_fixed:
        lon += bar_position_fixed[row["Country"]][0]
        lat += bar_position_fixed[row["Country"]][1]

    offsets = np.linspace(-bar_spacing, bar_spacing, len(vals))
    for i, (val, offset) in enumerate(zip(vals_scaled, offsets)):
        fig.add_trace(go.Scatter(
            x=[lon + offset, lon + offset],
            y=[lat, lat + val],
            mode="lines",
            line=dict(color=bar_colors[i], width=6),
            name=scenario_labels[i] if idx==0 else None,
            showlegend=(idx==0)
        ))

# ---------- LAYOUT ----------
fig.update_xaxes(range=[-25, 40])
fig.update_yaxes(range=[30, 65])
fig.update_layout(
    width=900, height=650,
    margin=dict(l=0,r=0,t=0,b=0),
)
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)

# Show figure
fig.show()


# only map MAP MAP MAP

# Create figure
fig = go.Figure()

# Add base layer: non-producing countries
non_prod_countries = excel_countries[excel_countries["color"] == pastel_colors["Non-Producing"]]
fig.add_trace(go.Choropleth(
    locations=non_prod_countries["ISO_A3"],
    z=[0]*len(non_prod_countries),
    colorscale=[[0, pastel_colors["Non-Producing"]], [1, pastel_colors["Non-Producing"]]],
    showscale=False,
    marker_line_color='white',
    marker_line_width=0.5,
    name="Not producing",
    showlegend=True
))

# Add producing countries (gray)
prod_countries = excel_countries[excel_countries["color"] == pastel_colors["Producing"]]
fig.add_trace(go.Choropleth(
    locations=prod_countries["ISO_A3"],
    z=[0]*len(prod_countries),
    colorscale=[[0, pastel_colors["Producing"]], [1, pastel_colors["Producing"]]],
    showscale=False,
    marker_line_color='white',
    marker_line_width=0.5,
    name="Producing European country",
    showlegend=True
))

# Ukraine separately
ukr_row = excel_countries[excel_countries["ISO_A3"]=="UKR"]
if not ukr_row.empty:
    color_type = "Producing" if (ukr_row[scenarios].values > 0).any() else "Non-Producing"
    fig.add_trace(go.Choropleth(
        geojson=ukraine_geojson,
        featureidkey="properties.GID_0",
        locations=ukr_row["ISO_A3"],
        z=[0],
        colorscale=[[0, pastel_colors[color_type]], [1, pastel_colors[color_type]]],
        showscale=False,
        marker_line_color='white',
        marker_line_width=0.5,
        name="Ukraine",
        showlegend=False
    ))


# Layout and legend
fig.update_geos(
    scope='world',
    projection_type='natural earth',
    showland=True,
    landcolor='rgb(240, 245, 255)',
    showcountries=True,
    countrycolor='rgb(180, 200, 230)',
    showcoastlines=True,
    coastlinecolor='rgb(160, 180, 220)',
    center=dict(lat=50, lon=20),
    lataxis=dict(range=[30, 65]),
    lonaxis=dict(range=[-25, 40]),
)

fig.update_layout(
        geo=dict(
            scope='world',  # or 'world'
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(220, 230, 250)',
            showcountries=True,
            countrycolor='rgb(180, 200, 230)',
            showcoastlines=True,
            coastlinecolor='rgb(160, 180, 220)',
            center=dict(lat=50, lon=20),
            lataxis=dict(range=[30, 65]),
            lonaxis=dict(range=[-25, 40]),
        ),
        legend=dict(
            x=0.965,  
            y=0.92,
            xanchor='right',
            yanchor='top',
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(0, 0, 0, 0.8)',
            borderwidth=1,
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        width=900,
        height=650
    )

# Show figure
fig.show()

# Save as image for background
map_image_path = "europe_map_background.png"
fig.write_image(map_image_path, width=900, height=650, engine="kaleido")

#now the bars: 

# Example: bar settings (from your code)
bar_height_scale = 7
bar_spacing = 0.7
bar_colors = ["#4f81bd", "#2ca02c", "#ca2e2e", "#732ca0"]
bar_position_fixed = {
    "Slovakia": (0.6, 0),
    "Hungary": (-0.6, 0),
    "Norway": (2, 0),
    "Germany": (1, 0)
}

scenario_labels = [
    "Reference Scenario",
    "Realized Expansion and Alternative resilience scenario",
    "Planned LNG Expansion Scenario (Stated Policies)",
    "Planned LNG Expansion Scenario (Announced Policies)"
]

# Create new figure
fig_bars = go.Figure()

# Add the saved map as background image
fig_bars.add_layout_image(
    dict(
        source=map_image_path,
        xref="x",
        yref="y",
        x=-25,           # match your x-axis range
        y=65,            # match your y-axis range (top)
        sizex=65,        # x_max - x_min
        sizey=35,        # y_max - y_min
        xanchor="left",
        yanchor="top",
        sizing="stretch",
        layer="below"
    )
)

# Example loop for adding bars
for idx, row in excel_countries.iterrows():
    iso3 = row["ISO_A3"]
    vals = np.array(row[scenarios], dtype=float)
    vals = np.nan_to_num(vals, nan=0.0)
    vals_scaled = np.sqrt(vals) / np.sqrt(vals.max()) * bar_height_scale

    lon, lat = get_country_coordinates(iso3)
    if row["Country"] in bar_position_fixed:
        lon += bar_position_fixed[row["Country"]][0]
        lat += bar_position_fixed[row["Country"]][1]

    offsets = np.linspace(-bar_spacing, bar_spacing, len(vals))
    for i, (val, offset) in enumerate(zip(vals_scaled, offsets)):
        fig_bars.add_trace(go.Scatter(
            x=[lon + offset, lon + offset],
            y=[lat, lat + val],
            mode="lines",
            line=dict(color=bar_colors[i], width=6),
            name=scenario_labels[i] if idx==0 else None,
            showlegend=(idx==0)
        ))

# Set axes to match map coordinates
fig_bars.update_xaxes(range=[-25, 40])
fig_bars.update_yaxes(range=[30, 65])
fig_bars.update_layout(
    width=900, height=650,
    margin=dict(l=0,r=0,t=0,b=0),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)

# Show figure
fig_bars.show()


#another approach
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.lines import Line2D
import numpy as np
import cartopy.crs as ccrs

# ---------- LOAD SAVED MAP ----------
map_img = mpimg.imread("europe_map_background.png")
img_height, img_width, _ = map_img.shape

fig, ax = plt.subplots(figsize=(img_width/100, img_height/100))
ax.imshow(map_img)  # default origin='upper'
ax.axis("off")

# ---------- NORMALIZE COORDINATES ----------
def normalize_coords(lon, lat, lon_min=-25, lon_max=40, lat_min=30, lat_max=65):
    x = (lon - lon_min) / (lon_max - lon_min) * img_width
    y = img_height - (lat - lat_min) / (lat_max - lat_min) * img_height
    return x, y

# ---------- GLOBAL OFFSET ----------
global_offset = -100  # negative moves bars left, positive moves right (in pixels)

# ---------- PLOT BARS ----------
bar_height_scale = 100  # adjust for visual scaling
bar_spacing = 1
bar_colors = ["#4f81bd", "#2ca02c", "#ca2e2e", "#732ca0"]

scenario_labels = [
    "Reference Scenario",
    "Realized Expansion and Alternative resilience scenario",
    "Planned LNG Expansion Scenario (Stated Policies)",
    "Planned LNG Expansion Scenario (Announced Policies)"
]

for idx, row in excel_countries.iterrows():
    iso3 = row["ISO_A3"]
    vals = np.array(row[scenarios], dtype=float)
    vals = np.nan_to_num(vals, nan=0.0)
    vals_scaled = np.sqrt(vals) / np.sqrt(vals.max()) * bar_height_scale

    lon, lat = get_country_coordinates(iso3)
    if row["Country"] in bar_position_fixed:
        lon += bar_position_fixed[row["Country"]][0]
        lat += bar_position_fixed[row["Country"]][1]

    offsets = np.linspace(-bar_spacing, bar_spacing, len(vals))
    for val, offset, color in zip(vals_scaled, offsets, bar_colors):
        x, y = normalize_coords(lon + offset, lat)
        x += global_offset  # apply global horizontal shift
        ax.plot([x, x], [y, y - val], color=color, linewidth=6)

# ---------- SCENARIO LEGEND (UPPER RIGHT) ----------
# Define all legend items: first the scenarios, then producing/non-producing
legend_colors = bar_colors + [pastel_colors["Producing"], pastel_colors["Non-Producing"]]
legend_labels = scenario_labels + ["Producing Country", "Non-Producing Country"]

# Create handles
legend_handles = [Line2D([0], [0], color=color, lw=4) for color in legend_colors]

# Add legend
ax.legend(
    legend_handles,
    legend_labels,
    loc='upper right',
    framealpha=0.8,
    fontsize=7,          # smaller font
    labelspacing=0.3,    # reduce spacing between labels
    handlelength=1.5,    # shorter line in legend
    handleheight=0.7,
    bbox_to_anchor=(1, 0.88)  # adjust vertical position
)

# ---------- SCALE LEGEND (LOWER RIGHT, MAX VALUE + FRACTIONS) ----------
def human_readable(val):
    if val >= 1_000_000:
        return f"{round(val/1_000_000,1)}M"
    elif val >= 1_000:
        return f"{round(val/1_000)}k"
    else:
        return str(int(val)) 

# Position in lower-right corner
legend_x = img_width * 0.85
legend_y_base = img_height * 0.95  # top of the bar

# Full height of the max value
val_height_max = bar_height_scale  # visual height of the maximum bar

# Draw the full bar for maximum value
ax.plot([legend_x, legend_x], [legend_y_base, legend_y_base - val_height_max],
        color='darkgrey', lw=6)

# Label the full max value
ax.text(legend_x + 5, legend_y_base - val_height_max,
        f"{human_readable(global_max_raw)} GWh/a",
        va='bottom', ha='left', color='black', fontsize=8)

# Fractions of max value for intermediate markers
scale_fracs = [0.25, 0.5, 0.75]

for frac in scale_fracs:
    frac_height = frac * val_height_max
    y_pos = legend_y_base - frac_height
    # Draw small marker line
    ax.plot([legend_x - 2, legend_x + 2], [y_pos, y_pos], color='black', lw=2)
    # Label the fraction
    ax.text(legend_x + 5, y_pos, f"{human_readable(frac * global_max_raw)}",
            va='center', ha='left', fontsize=7, color='black')

plt.show()