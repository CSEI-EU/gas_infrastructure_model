# plotly_map_bars_fixed.py
import os
import json
import geopandas as gpd
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from shapely.geometry import mapping

# -------------------------
# Config
save_output = False
scenarios = ["2021", "2024", "2035 High Demand"]
input_file_path = os.path.join('01_data', '01_input_data', '02_processed', '01_paper_IAEE', '01_data_sheets_input')
input_file = '\\paper_paris_2025_input_production_world.xlsx'
full_input_path = os.path.abspath(os.path.join(os.getcwd(), input_file_path + input_file))
output_path = os.path.join('02_plots')

# shapefile path
shapefile_path = os.path.join('01_data', '01_input_data', '01_raw', 'world_countries_shapefile')
shapefile = '\\ne_50m_admin_0_countries_lakes.shp'
full_shapefile_path = os.path.abspath(os.path.join(os.getcwd(), shapefile_path + shapefile))

# -------------------------
# Load data
data_gas_prod = pd.read_excel(full_input_path)

# -------------------------
# Fix Crimea (Ukraine polygon)
ukraine_json_url = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_UKR_0.json"
ukraine_json_path = os.path.join("00_code_base", "08_output_preparation", "gadm41_UKR_0.json")
resp = requests.get(ukraine_json_url)
resp.raise_for_status()
os.makedirs(os.path.dirname(ukraine_json_path), exist_ok=True)
with open(ukraine_json_path, "wb") as f:
    f.write(resp.content)
ukraine_corrected = gpd.read_file(ukraine_json_path)

# Load world shapefile
world = gpd.read_file(full_shapefile_path)
world = world[world["NAME"] != "Ukraine"]
ukraine_corrected = ukraine_corrected.rename(columns={"GID_0":"ISO_A3", "NAME_0":"NAME"})
world = pd.concat([world, ukraine_corrected], ignore_index=True)

# Fix ISO errors
fix_iso = {"France": "FRA", "Norway": "NOR", "Kosovo": "XKX"}
world["ISO_A3"] = world.apply(lambda row: fix_iso.get(row["NAME"], row.get("ISO_A3")), axis=1)
world = world[world["CONTINENT"] != "Antarctica"]

# Remove Crimea from Russia (optional)
russia_idx = world['ISO_A3'] == "RUS"
ukraine_idx = world['ISO_A3'] == "UKR"
if not world.loc[russia_idx, 'geometry'].empty and not world.loc[ukraine_idx, 'geometry'].empty:
    try:
        russia_geom = world.loc[russia_idx, 'geometry'].values[0]
        ukraine_geom = world.loc[ukraine_idx, 'geometry'].values[0]
        world.loc[russia_idx, 'geometry'] = russia_geom.difference(ukraine_geom)
    except Exception:
        pass

# -------------------------
# Define regions and colors
region_to_countries = {
    "Africa": world[world["CONTINENT"] == "Africa"]["ISO_A3"].tolist(),
    "Oceania": world[world["CONTINENT"] == "Oceania"]["ISO_A3"].tolist(),
    "Australia": ["AUS", "NZL"],
    "South America": world[world["CONTINENT"] == "South America"]["ISO_A3"].tolist(),
    "North America": world[world["CONTINENT"] == "North America"]["ISO_A3"].tolist(),
    "Caspian Region": ["AZE", "KAZ", "UZB", "KGZ", "TKM", "TJK", "GEO"],
    "Middle East": ["SAU", "QAT", "UAE", "KWT", "OMN", "IRQ", "ISR", "JOR", "SYR", "LBN", "YEM", "ARE", "IRN"],
    "Indonesia & Malaysia": ["IDN", "MYS"],
    "Japan & South Korea": ["JPN", "KOR"],
    "Algeria": ["DZA"],
    "China": ["CHN"],
    "Egypt": ["EGY"],
    "India": ["IND"],
    "Libya": ["LBA"],
    "Morroco": ["MAR"],
    "Qatar": ["QAT"],
    "Russia": ["RUS"],
    "Trinidad & Tobago": ["TTO"],
    "Tunisia": ["TUN"],
    "USA": ["USA"],
    "Ukraine": ["UKR"]
}
asia_exclusions = ["TUR"] + region_to_countries["Middle East"] + region_to_countries["Caspian Region"]
region_to_countries["Asia"] = [c for c in world[world["CONTINENT"] == "Asia"]["ISO_A3"].tolist() if c not in asia_exclusions] + ["PNG"]
region_to_countries["Oceania"] = ["AUS", "NZL"]

specific_regions = [
    "Africa", "North America", "South America",
    "Middle East", "Asia", "Russia", "Australia", "Caspian Region"
]
pastel_colors = {
    "Africa": "#c7e9c0",
    "North America": "#bae4f5",
    "South America": "#7cc2f3",
    "Middle East": "#fdd0a2",
    "Caspian Region": "#fdae6b",
    "Asia": "#fcbba1",
    "Russia": "#fee6ce",
    "Australia": "#dadaeb",
}
highlight_countries = {
    "USA": "#2e8ccf", "TTO": "#2e3bcf", "QAT": "#e6550d",
    "DZA": "#247143", "EGY": "#247143", "MAR": "#247143", "LBY": "#247143", "TUN": "#247143",
    "MYS": "#e36c3d", "IND": "#e36c3d", "CHN": "#e36c3d", "HKG": "#e36c3d",
    "KOR": "#dd7762", "JPN": "#dd7762",
}

# -------------------------
# Prepare GeoJSON
world_for_geo = world.copy()
features = []
for _, row in world_for_geo.iterrows():
    geom = row.geometry
    if geom is None or geom.is_empty:
        continue
    features.append({
        "type": "Feature",
        "geometry": mapping(geom),
        "properties": {
            "ISO_A3": row.get("ISO_A3"),
            "NAME": row.get("NAME"),
            "CONTINENT": row.get("CONTINENT")
        }
    })
geojson = {"type": "FeatureCollection", "features": features}

# region index for coloring
region_index_map = {r: i+1 for i, r in enumerate(specific_regions)}
region_palette = [pastel_colors[r] for r in specific_regions]
iso_to_region_idx = {}
for r in specific_regions:
    for iso in region_to_countries.get(r, []):
        iso_to_region_idx[iso] = region_index_map[r]

locations, z = [], []
for feat in geojson["features"]:
    iso = feat["properties"]["ISO_A3"]
    locations.append(iso)
    z.append(iso_to_region_idx.get(iso, 0))

# -------------------------
# Compute centroids & bar scaling
vals_for_scaling = data_gas_prod.loc[data_gas_prod['Country'] != "Total", scenarios].values.flatten()
vals_for_scaling = np.array(vals_for_scaling, dtype=float)
global_max_raw = vals_for_scaling.max()
global_max_sqrt = np.sqrt(global_max_raw)

# centroids
region_centroids = {}
for region_name in specific_regions:
    if region_name not in region_to_countries:
        continue
    countries = region_to_countries[region_name]
    region_gdf = world_for_geo[world_for_geo['ISO_A3'].isin(countries)]
    if region_gdf.empty:
        continue
    centroid = region_gdf.unary_union.centroid
    region_centroids[region_name] = (centroid.x, centroid.y)

# lat span for bar degree scaling
all_lats = [pt.y for pt in world_for_geo.geometry.centroid]
lat_span = max(all_lats) - min(all_lats) if all_lats else 60.0
max_bar_deg = lat_span * 0.05  # 5% of map height
scale_factor = 10.0
deg_per_unit = max_bar_deg / scale_factor
scenario_colors = ["#4f81bd", "#2ca02c", "#ca2e2e"]

# -------------------------
# Build bar traces
bar_traces = []
bar_width_deg = 0.5
for region_name, centroid in region_centroids.items():
    lon_c, lat_c = centroid
    if region_name in data_gas_prod['Country'].values:
        vals = np.array(data_gas_prod.loc[data_gas_prod['Country'] == region_name, scenarios].values.flatten(), dtype=float)
    else:
        vals = np.zeros(len(scenarios))
    vals_sqrt = np.sqrt(vals)
    vals_scaled = vals_sqrt / global_max_sqrt * scale_factor
    vals_scaled = np.clip(vals_scaled, 0, scale_factor)  # safety clip

    for i, v in enumerate(vals_scaled):
        h_deg = min(v * deg_per_unit, max_bar_deg)
        x_offset = (i - 1) * (bar_width_deg + 0.1)
        left = max(-180, min(180, lon_c + x_offset - bar_width_deg/2))
        right = max(-180, min(180, lon_c + x_offset + bar_width_deg/2))
        bottom = max(-90, min(90, lat_c))
        top = max(-90, min(90, lat_c + h_deg))
        polygon_lons = [left, right, right, left, left]
        polygon_lats = [bottom, bottom, top, top, bottom]

        trace = go.Scattergeo(
            lon=list(polygon_lons),
            lat=list(polygon_lats),
            mode='lines',
            fill='toself',
            fillcolor=scenario_colors[i],
            line=dict(width=0.5, color='black'),
            name=scenarios[i],
            showlegend=False,
            hoverinfo='text',
            text=f"{region_name} — {scenarios[i]}: {int(vals[i]):,}"
        )
        bar_traces.append(trace)

# -------------------------
# Choropleth
colorscale = [[(i+1)/(len(region_palette)+1), c] for i, c in enumerate(region_palette)]
choropleth = go.Choropleth(
    geojson=geojson,
    locations=locations,
    z=z,
    colorscale=colorscale,
    zmin=0,
    zmax=len(region_palette)+1,
    marker_line_color='grey',
    marker_line_width=0.3,
    showscale=False,
    hoverinfo='location'
)

# Legend dummies
legend_traces = [go.Scattergeo(lon=[None], lat=[None], mode='markers', marker=dict(size=10, color=c), name=r)
                 for r, c in zip(specific_regions, region_palette)]

# Highlight countries
highlight_traces = []
for iso, col in highlight_countries.items():
    g = world_for_geo[world_for_geo['ISO_A3'] == iso]
    if g.empty:
        continue
    boundary = g.geometry.boundary
    for geom in boundary:
        if geom.geom_type == "MultiLineString":
            for part in geom.geoms:
                xs, ys = list(part.xy[0]), list(part.xy[1])
                highlight_traces.append(go.Scattergeo(lon=xs, lat=ys, mode='lines', line=dict(color=col, width=1.5), showlegend=False))
        else:
            xs, ys = list(geom.xy[0]), list(geom.xy[1])
            highlight_traces.append(go.Scattergeo(lon=xs, lat=ys, mode='lines', line=dict(color=col, width=1.5), showlegend=False))

# -------------------------
# Build figure
fig = go.Figure()
fig.add_trace(choropleth)
for t in legend_traces + bar_traces + highlight_traces:
    fig.add_trace(t)
for s, c in zip(scenarios, scenario_colors):
    fig.add_trace(go.Scattergeo(lon=[None], lat=[None], mode='markers', marker=dict(size=12, color=c), name=s))

fig.update_geos(showcountries=False, showcoastlines=True, coastlinecolor="rgb(200,200,200)", projection_type="equirectangular")
fig.update_layout(title_text="World map with bar-plots at region centroids", legend_title_text="Scenarios & Regions", margin={"r":0,"t":40,"l":0,"b":0}, height=800, width=1400)

# Show or save
fig.show()
if save_output:
    os.makedirs(output_path, exist_ok=True)
    html_out = os.path.join(output_path, "world_map_bar_plotly.html")
    fig.write_html(html_out)