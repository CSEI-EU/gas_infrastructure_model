import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import json
from shapely.geometry import shape
import shapely
from math import cos, radians
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import cartopy.crs as ccrs
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

legend_in_bars = True  # set False if you want the map legend visible
save_output = False
scenarios = ["2021", "2024", "2035 High Demand", "2035 Low Demand"]

# base_path = r"C:\Users\jfg.eco\Documents\hydrogen_grid"
base_path = r"C:\Users\mar.eco\OneDrive - CBS - Copenhagen Business School\Desktop\hydrogen_grid"


# Input data
input_file_path = os.path.join(base_path, '01_data', '01_input_data', '02_processed', '01_paper_IAEE', '01_data_sheets_input')
input_file = 'paper_paris_2025_input_consumption_europe.xlsx'
# input_file = 'paper_paris_2025_input_production_europe_capacities.xlsx'
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

# Correct typo in Country column
data_gas_prod["Country"] = data_gas_prod["Country"].replace({"Irland": "Ireland"})

# Exclude Total row for plot and calculations
excel_countries = data_gas_prod[data_gas_prod["Country"] != "Total"].copy()

# Output path and names
output_path = "02_plots"
output_svg_name = "europe_map_background.svg"
map_image_name = "europe_map_background.png"

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
    return pastel_colors["Producing"] if np.any(vals != 0) else pastel_colors["Non-Producing"]

excel_countries["color"] = excel_countries.apply(country_color, axis=1)

# Bar scaling setup
vals_for_scaling = excel_countries[scenarios].values.flatten()
global_max_raw = np.max(np.abs(vals_for_scaling))
global_max_sqrt = np.sqrt(global_max_raw)
bar_height_scale = 1
bar_colors = ["#4f81bd", "#2ca02c", "#ca2e2e", "#732ca0"]
bar_spacing = 0.6



# Country coordinates
COUNTRY_COORDINATES = {
    'ALB': (20.1683, 41.1533), 'AUT': (14.5501, 47.5162), 'BLR': (27.9534, 53.7098),
    'BEL': (4.3517, 50.8503), 'BIH': (17.6791, 43.9159), 'BGR': (25.4858, 42.7339),
    'HRV': (15.2, 45.1), 'CZE': (15.4730, 49.8175), 'DNK': (9.5018, 55.2639),
    'EST': (25.0136, 58.5953), 'FIN': (25.7482, 61.9241), 'FRA': (1.8883, 46.6034),
    'DEU': (10.4515, 51.1657), 'GRC': (21.8243, 39.0742), 'HUN': (19.5033, 47.1625),
    'IRL': (-7.6921, 53.1424), 'ITA': (12.5674, 41.8719), 'LVA': (24.6032, 56.8796),
    'LTU': (23.8813, 55.1694), 'LUX': (6.1296, 49.8153), 'MDA': (28.3699, 47.4116),
    'NLD': (5.2913, 52.1326), 'MKD': (21.4254, 41.9981), 'NOR': (6.7, 58.4720),
    'POL': (19.1451, 51.9194), 'PRT': (-8.2245, 39.3999), 'ROU': (24.9668, 45.9432),
    'SRB': (21.0059, 44.0165), 'SVK': (19.6990, 48.6690), 'SVN': (14.9955, 46.1512),
    'ESP': (-3.7492, 40.4637), 'CHE': (8.2275, 46.8182), 'TUR': (35.0, 39.0),
    'GBR': (-1.5, 51.0), 'UKR': (31.1656, 48.3794), 'XKX': (20.9020, 42.6026),
    'SWE': (14.5, 58), 'MNE': (19.3744, 42.7087), 'MLT': (14.3754, 35.9375)
}

def get_country_coordinates(iso3):
    return COUNTRY_COORDINATES.get(iso3, (10, 50))

# ---------- HUMAN READABLE FUNCTION ----------
def human_readable(val):
    """Convert large numbers to readable strings with k/M suffix."""
    if val >= 1_000_000:
        return f"{round(val/1_000_000,1)}M"
    elif val >= 1_000:
        return f"{round(val/1_000)}k"
    else:
        return str(int(val))

# --- Reference country pixel position on the map ---
REFERENCE_COUNTRY = "DEU"
REFERENCE_TARGET_PIXEL = (320, 300)  # (x, y) position of Germany on your map image

# --- Convert all countries from lon/lat → normalized pixel coordinates ---
def normalize_coords(lon, lat):
    x = (lon - lon_min) / (lon_max - lon_min) * img_width
    y = img_height - (lat - lat_min) / (lat_max - lat_min) * img_height
    return np.array([x, y])

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


# Plot only the MAP and export

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
    showlegend=not legend_in_bars   # <-- toggle legend visibility
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
    showlegend=not legend_in_bars   # <-- toggle legend visibility
))

# Ukraine separately (if applicable)
ukr_row = excel_countries[excel_countries["ISO_A3"] == "UKR"]
if not ukr_row.empty:
    color_type = "Producing" if (ukr_row[scenarios].values != 0).any() else "Non-Producing"
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

# Define legend layout separately for consistent handling
legend_layout = None
if not legend_in_bars:
    legend_layout = dict(
        x=0.965,
        y=0.92,
        xanchor='right',
        yanchor='top',
        bgcolor='rgba(255, 255, 255, 0.8)',
        bordercolor='rgba(0, 0, 0, 0.8)',
        borderwidth=1,
    )

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
        lonaxis=dict(range=[-25, 40]),
    ),
    legend=legend_layout,
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    width=900,
    height=650
)

# Disable legend completely
for trace in fig.data:
    trace.showlegend = False

# Also remove layout legend (just to be safe)
fig.update_layout(legend=dict(
    x=0, y=0, visible=False
))

# Show figure
# fig.show()

# Save as image for background
fig.write_image(map_image_name, width=900, height=650, engine="kaleido")
fig.write_image(output_svg_name, format="svg")


# ---------- LOAD SAVED MAP ----------
map_img = mpimg.imread("europe_map_background.png")
img_height, img_width, _ = map_img.shape

fig, ax = plt.subplots(figsize=(img_width/100, img_height/100))
ax.imshow(map_img)  # default origin='upper'
ax.axis("off")

# ---------- GLOBAL OFFSET ----------
global_offset = 10  # negative moves bars left, positive moves right (in pixels)

#adjust coordinates for bar plots
# --- Geographic bounding box of the map (used for normalization) ---
lon_min, lon_max = -25, 40
lat_min, lat_max = 30, 65

# Compute where the reference country currently appears
lon_ref, lat_ref = COUNTRY_COORDINATES[REFERENCE_COUNTRY]
ref_current = normalize_coords(lon_ref, lat_ref)

# Compute pixel offset to move Germany into correct place
offset = np.array(REFERENCE_TARGET_PIXEL) - ref_current

# Apply this same offset to all other countries
COUNTRY_COORDINATES_ADJUSTED = {
    iso: tuple(normalize_coords(lon, lat) + offset)
    for iso, (lon, lat) in COUNTRY_COORDINATES.items()
}

manual_offsets = {
    "DEU": (0, 20),       
    "IRL": (5, 0),         
    "DNK": (0, 5),         
    "NOR": (20, 0),        
    "FIN": (-20, 10),     
    "EST": (-5, 20),       
    "LVA": (-5, 20),    
    "LTU": (-10, 25), 
    "NLD": (0, -10),
    "SVN": (-5, -5), 
    "BIH": (0, -5), 
    "SRB": (0, -10), 
    "ALB": (-5, 0), 
    "MNE": (-5, 0), 
    "MKD": (5, 0),
    "SVK": (0, -10), 
    "HUN": (-5, 5),
}

# Apply the offsets
for iso, (dx, dy) in manual_offsets.items():
    if iso in COUNTRY_COORDINATES_ADJUSTED:
        x, y = COUNTRY_COORDINATES_ADJUSTED[iso]
        COUNTRY_COORDINATES_ADJUSTED[iso] = (x + dx, y + dy)

# ---------- PLOT BARS ----------
bar_height_scale = 60
bar_spacing = 15
bar_colors = ["#4f81bd", "#2ca02c", "#ca2e2e", "#732ca0"]
scenario_labels = [
    "Reference Scenario",
    "Realized Expansion and Alternative Resilience Scenario",
    "Planned LNG Expansion Scenario (SP)",
    "Planned LNG Expansion Scenario (AP)"
]

for idx, row in excel_countries.iterrows():
    iso3 = row["ISO_A3"]
    vals = np.array(row[scenarios], dtype=float)
    vals = np.nan_to_num(vals, nan=0.0)
    vals_scaled = np.sqrt(np.abs(vals)) / global_max_sqrt * bar_height_scale

    x, y = COUNTRY_COORDINATES_ADJUSTED.get(iso3, (None, None))
    if x is None:
        continue

    offsets = np.linspace(-bar_spacing, bar_spacing, len(vals_scaled))
    for val, offset, color in zip(vals_scaled, offsets, bar_colors):
        x_offset = x + offset + global_offset
        ax.plot([x_offset, x_offset], [y, y - val], color=color, linewidth=6)

# ---------- SCENARIO + COUNTRY LEGEND ----------

# Bar colors for scenarios
legend_scenarios = [Patch(facecolor=color, label=label) for color, label in zip(bar_colors, scenario_labels)]

# Circles for Producing / Non-Producing
legend_countries = [
    Line2D([0], [0], marker='o', color='w', label='Producing Country', 
           markerfacecolor=pastel_colors["Producing"], markersize=8),
    Line2D([0], [0], marker='o', color='w', label='Non-Producing Country', 
           markerfacecolor=pastel_colors["Non-Producing"], markersize=8)
]

# Combine all handles
handles_legend = legend_scenarios + legend_countries

# Place legend a bit higher and layout as 2 rows x 3 columns
ax.legend(
    handles=handles_legend,
    loc="lower center",
    bbox_to_anchor=(0.5, 0.06),
    ncol=3,                       # 3 columns
    frameon=True,
    fontsize=7
)

# ---------- SCALE LEGEND (bar heights, left side) ----------
# Create inset axes
axins = inset_axes(
    ax,
    width="2%",       # thin vertical bar
    height="25%",     # relative height
    loc="lower right", 
    bbox_to_anchor=(-0.05, 0.3, 1, 1), # position on figure
    bbox_transform=ax.transAxes,
    borderpad=0
)

# Bar height scale
scale_factor = bar_height_scale  # max visual bar height

# Draw a single grey bar to show the max height
axins.bar(0, scale_factor, width=0.6, color="lightgrey")

# Tick values and labels
tick_vals = np.linspace(0, scale_factor, 5)
tick_labels = [human_readable((val / scale_factor)**2 * global_max_raw) for val in tick_vals]

# Set ticks
axins.set_ylim(0, scale_factor)
axins.set_xticks([])
axins.set_yticks(tick_vals)
axins.set_yticklabels(tick_labels, fontsize=8)

# Optional title above the scale
axins.set_title("GWh/a", fontsize=9)
axins.set_frame_on(False)  # hide inset frame

plt.show()

# Save the figure to files
output_png_path = os.path.join(output_path, "europe_map_with_bars.png")
output_svg_path = os.path.join(output_path, "europe_map_with_bars.svg")

fig.savefig(output_png_path, dpi=900, bbox_inches='tight')
fig.savefig(output_svg_path, format='svg', bbox_inches='tight')