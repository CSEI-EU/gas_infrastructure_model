import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import json

save_output = True
scenarios = ["2021", "2024", "2035 High Demand", "2035 Low Demand"]

# Input data
input_file_path = os.path.join('01_data', '01_input_data', '02_processed', '01_paper_IAEE', '01_data_sheets_input')
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
excel_countries = [c for c in data_gas_prod["Country"].unique() if c != "Total"]

# Output path
output_path = "02_plots"

# Fix all countries names
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
data_gas_prod["ISO_A3"] = data_gas_prod["Country"].map(country_name_to_iso3)

# Pastel colors 
pastel_colors = {"Producing": "#b5b4b4", "Non-Producing": "#DFDFDF"}
def country_color(row):
    vals = row[scenarios].values
    return pastel_colors["Producing"] if np.any(vals > 0) else pastel_colors["Non-Producing"]
data_gas_prod["color"] = data_gas_prod.apply(country_color, axis=1)

# Find global max
vals_for_scaling = data_gas_prod.loc[data_gas_prod['Country'] != "Total", scenarios].values.flatten()
global_max_raw = np.max(vals_for_scaling)
global_max_sqrt = np.sqrt(global_max_raw)
bar_height_scale = 6
bar_colors = ["#4f81bd", "#2ca02c", "#ca2e2e", "#732ca0"]
bar_spacing = 0.7
bar_position_fixed = {"Slovakia": (0.6, 0), "Hungary": (-0.6, 0), "Norway": (-6, -4)}


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
    return COUNTRY_COORDINATES.get(iso3, (10, 50))  # fallback to central Europe

# Fix Crimea handling
ukraine_json_url = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_UKR_0.json"
ukraine_json_path = os.path.join("00_code_base", "08_output_preparation", "gadm41_UKR_0.json")
if not os.path.exists(ukraine_json_path):
    os.makedirs(os.path.dirname(ukraine_json_path), exist_ok=True)
    with open(ukraine_json_path, "wb") as f:
        f.write(requests.get(ukraine_json_url).content)
with open(ukraine_json_path, "r", encoding="utf-8") as f:
    ukraine_geojson = json.load(f)

from shapely.geometry import shape
import shapely

def get_centroid_from_geojson(geojson_feature):
    geom = shape(geojson_feature["geometry"])
    if isinstance(geom, shapely.geometry.multipolygon.MultiPolygon):
        largest = max(geom.geoms, key=lambda p: p.area)
        return largest.centroid
    else:
        return geom.centroid

# Create the figure
fig = go.Figure()

# Europe base map
fig.add_trace(go.Choropleth(
    locations=data_gas_prod["ISO_A3"],
    z=np.zeros(len(data_gas_prod)),
    colorscale=[[0, "lightgrey"], [1, "lightgrey"]],
    showscale=False,
    marker_line_color='white',
    marker_line_width=0.5,
    name="Europe"
))

# Ukraine separately
ukr_row = data_gas_prod[data_gas_prod["ISO_A3"]=="UKR"]
if not ukr_row.empty:
    fig.add_trace(go.Choropleth(
        geojson=ukraine_geojson,
        featureidkey="properties.GID_0",
        locations=ukr_row["ISO_A3"],
        z=[0],
        colorscale=[[0, "lightgrey"], [1, "lightgrey"]],
        showscale=False,
        marker_line_color='white',
        marker_line_width=0.5,
        name="Ukraine"
    ))

# Bar plot 
for idx, row in data_gas_prod.iterrows():
    iso3 = row["ISO_A3"]
    vals = np.array(row[scenarios], dtype=float)
    vals = np.nan_to_num(vals, nan=0.0)
    vals_scaled = np.sqrt(vals) / global_max_sqrt * bar_height_scale

    # Centroid
    if iso3 == "UKR":
        centroid = get_centroid_from_geojson(ukraine_geojson["features"][0])
        x, y = centroid.x, centroid.y
    else:
        lon, lat = get_country_coordinates(iso3)
        x, y = lon, lat

    # Apply small manual offsets
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
            showlegend=(idx==0),
            name=(scenarios[i] if idx==0 else None)
        ))


fig.update_geos(
    showland=True,
    landcolor='rgb(220, 230, 250)',
    showcountries=True,
    countrycolor='rgb(180, 200, 230)',
    showcoastlines=True,
    coastlinecolor='rgb(160, 180, 220)',
    projection_type='natural earth',
    center=dict(lat=55, lon=15),
    lataxis_range=[34,72],
    lonaxis_range=[-25,45]
)
fig.update_layout(height=800, width=1135, margin={"r":0,"t":0,"l":0,"b":0})

# Show or save
if save_output:
    os.makedirs(output_path, exist_ok=True)
    fig.write_image(os.path.join(output_path, "europe_bar_plot_simple.png"), width=1135, height=800, scale=2)
else:
    fig.show()
