import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import json
from shapely.geometry import shape
import shapely

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
ukraine_json_path = os.path.join("00_code_base", "08_output_preparation", "gadm41_UKR_0.json")
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
