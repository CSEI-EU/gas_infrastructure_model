import os
import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Change parameters for output 
save_output = True
scenarios = ["2021", "2024", "2035 High Demand"] #, "2035 Low Demand"] 

# Input data
input_file_path = os.path.join('01_data', '01_input_data', '02_processed', '01_paper_IAEE', '01_data_sheets_input')
input_file = '\\paper_paris_2025_input_consumption_world.xlsx' # Change to production or consumption
title_plot = "world_map_bar_plotly_cons.png"
full_input_path = os.path.abspath(os.path.join(os.getcwd(), input_file_path + input_file))
data_gas_prod = pd.read_excel(full_input_path)

# LNG port locations 
LNG_location_path = os.path.join('01_data', '01_input_data', '01_raw', '01_Russian_War_Case')
LNG_file = '\\LNG_locations.xlsx'
full_LNG_path = os.path.abspath(os.path.join(LNG_location_path + LNG_file))
ports_df = pd.read_excel(full_LNG_path, sheet_name="Global")

# Convert locations to float
ports_df['Latitude'] = ports_df['Latitude'].astype(str).str.replace(',', '.').astype(float)
ports_df['Longitude'] = ports_df['Longitude'].astype(str).str.replace(',', '.').astype(float)

# Output path
output_path = os.path.join('02_plots')

# World shapefile
shapefile_path = os.path.join('01_data', '01_input_data', '01_raw', 'world_countries_shapefile')
shapefile = '\\ne_50m_admin_0_countries_lakes.shp'
full_shapefile_path = os.path.abspath(os.path.join(os.getcwd(), shapefile_path + shapefile))

# Load world shapefile
world = gpd.read_file(full_shapefile_path)
world = world[world["CONTINENT"] != "Antarctica"]  # remove Antarctica

# Fix ISO codes
fix_iso = {"France": "FRA", "Norway": "NOR", "Kosovo": "XKX"}
world["ISO_A3"] = world.apply(lambda row: fix_iso.get(row["NAME"], row["ISO_A3"]), axis=1)


# Define regions and colors
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

region_to_countries = {
    "Africa": world[world["CONTINENT"] == "Africa"]["ISO_A3"].tolist(),
    "North America": world[world["CONTINENT"] == "North America"]["ISO_A3"].tolist(),
    "South America": world[world["CONTINENT"] == "South America"]["ISO_A3"].tolist(),
    "Asia": [c for c in world[world["CONTINENT"] == "Asia"]["ISO_A3"].tolist() if c not in ["TUR"]] + ["PNG"],
    "Australia": ["AUS", "NZL"],
    "Caspian Region": ["AZE", "KAZ", "UZB", "KGZ", "TKM", "TJK", "GEO"],
    "Middle East": ["SAU", "QAT", "UAE", "KWT", "OMN", "IRQ", "ISR", "JOR", "SYR", "LBN", "YEM", "ARE", "IRN"],
    "Russia": ["RUS"],
}

highlight_countries = {
    "USA": "#2e8ccf", "TTO": "#2e3bcf", "QAT": "#e6550d",
    "DZA": "#247143", "EGY": "#247143", "MAR": "#247143", "LBY": "#247143", "TUN": "#247143",
    "MYS": "#e36c3d", "IND": "#e36c3d", "CHN": "#e36c3d", "HKG": "#e36c3d", "IDN": "#e36c3d",
    "KOR": "#dd7762", "JPN": "#dd7762",
}


# Map ISO codes to corresponding color
iso_to_color = {}
for region, isos in region_to_countries.items():
    color = pastel_colors.get(region, "#cccccc")
    for iso in isos:
        iso_to_color[iso] = color

for iso in region_to_countries["Africa"]:  # force all Africa to be green
    iso_to_color[iso] = pastel_colors["Africa"]

world["fill_color"] = world["ISO_A3"].map(iso_to_color).fillna("#e0e0e0")


# Build figure
fig = go.Figure()

# Plot countries
for _, row in world.iterrows():
    geom = row.geometry
    color = row["fill_color"]
    if geom is None or geom.is_empty:
        continue
    if geom.geom_type == "MultiPolygon":
        for part in geom.geoms:
            lon, lat = list(part.exterior.xy[0]), list(part.exterior.xy[1])
            fig.add_trace(go.Scattergeo(lon=lon, lat=lat, mode="lines", fill="toself",
                                        fillcolor=color, line=dict(color="grey", width=0.5), showlegend=False))
    else:
        lon, lat = list(geom.exterior.xy[0]), list(geom.exterior.xy[1])
        fig.add_trace(go.Scattergeo(lon=lon, lat=lat, mode="lines", fill="toself",
                                    fillcolor=color, line=dict(color="grey", width=0.5), showlegend=False))

# Outlined countries
for iso, col in highlight_countries.items():
    g = world[world["ISO_A3"] == iso]
    if g.empty:
        continue
    for geom in g.geometry:
        if geom.geom_type == "MultiPolygon":
            for part in geom.geoms:
                lon, lat = list(part.exterior.xy[0]), list(part.exterior.xy[1])
                fig.add_trace(go.Scattergeo(lon=lon, lat=lat, mode='lines',
                                            line=dict(color=col, width=2), showlegend=False))
        else:
            lon, lat = list(geom.exterior.xy[0]), list(geom.exterior.xy[1])
            fig.add_trace(go.Scattergeo(lon=lon, lat=lat, mode='lines',
                                        line=dict(color=col, width=2), showlegend=False))

# LNG ports
fig.add_trace(go.Scattergeo(
    lon=ports_df["Longitude"].tolist(),
    lat=ports_df["Latitude"].tolist(),
    mode="markers",
    marker=dict(size=6, color="black"),
    name="LNG Ports"
))

vals_for_scaling = data_gas_prod.loc[data_gas_prod['Country'] != "Total", scenarios].values.flatten()
vals_for_scaling = np.array(vals_for_scaling, dtype=float)
global_max_raw = vals_for_scaling.max()
global_max_sqrt = np.sqrt(global_max_raw)
bar_height_scale = 28
bar_colors = ["#4f81bd", "#2ca02c", "#ca2e2e"]
bar_spacing = 3

bar_position_fixed = {
    "North America": (-98.5, 39.8),
    "Middle East": (41.50, 27.6)
}

for region_name, isos in region_to_countries.items():
    if region_name not in data_gas_prod['Country'].values:
        continue

    region_geom = world[world['ISO_A3'].isin(isos)]
    if region_geom.empty:
        continue

    if region_name in bar_position_fixed:
        x, y = bar_position_fixed[region_name]
    else:
        centroid = region_geom.unary_union.centroid
        x, y = centroid.x, centroid.y

    vals = data_gas_prod.loc[data_gas_prod['Country'] == region_name, scenarios].values.flatten()
    vals_scaled = np.sqrt(vals) / global_max_sqrt * bar_height_scale

    offsets = np.linspace(-bar_spacing, bar_spacing, len(vals))
    for i, (val, offset) in enumerate(zip(vals_scaled, offsets)):
        fig.add_trace(go.Scattergeo(
            lon=[x + offset, x + offset],
            lat=[y, y + val],
            mode="lines",
            line=dict(color=bar_colors[i], width=8),
            showlegend=(region_name == list(region_to_countries.keys())[0]),
            name=(
    {
        "2021": "Reference Scenario",
        "2024": "Realized Expansion and<br>Alternative resilience scenario",
        "2035 High Demand": "Planned LNG Expansion<br>Scenario with the Ap and SP variation"
    }[scenarios[i]]
    if (region_name == list(region_to_countries.keys())[0])
    else None
)
        ))

# Add bar height legend
scale_lon, scale_lat = -150, -50
scale_vals = [0, int(global_max_raw/2), int(global_max_raw)]

def human_readable(val):
    if val >= 1_000_000:
        return f"{round(val/1_000_000,1)}M"
    elif val >= 1_000:
        return f"{round(val/1_000)}k"
    else:
        return str(int(val))

for val in scale_vals:
    fig.add_trace(go.Scattergeo(
        lon=[scale_lon, scale_lon],
        lat=[scale_lat, scale_lat + np.sqrt(val)/global_max_sqrt*bar_height_scale],
        mode="lines",
        line=dict(color="darkgrey", width=8),
        showlegend=False
    ))
    fig.add_trace(go.Scattergeo(
        lon=[scale_lon - 15],
        lat=[scale_lat + np.sqrt(val)/global_max_sqrt*bar_height_scale],
        mode="text",
        text=[f"{human_readable(val)} GWh/a"],
        showlegend=False,
        textfont=dict(size=10)
    ))

# Legend for regions color and items
for region_name, color in pastel_colors.items():
    label = "Oceania" if region_name == "Australia" else region_name
    fig.add_trace(go.Scattergeo(
        lon=[None], lat=[None],
        mode="markers",
        marker=dict(size=10, color=color, line=dict(width=0.5, color="grey")),
        showlegend=True,
        name=label
    ))

fig.add_trace(go.Scattergeo(
    lon=[None],
    lat=[None],
    mode="lines",
    line=dict(color="black", width=1),
    name="Model nodes (outlined countries)",
    showlegend=True
))


# Similar layout to previous maps
fig.update_geos(
    showland=True,
    landcolor='rgb(220, 230, 250)',
    showcountries=True,
    countrycolor='rgb(180, 200, 230)',
    showcoastlines=True,
    coastlinecolor='rgb(160, 180, 220)',
    projection_type='equirectangular'   #used natural earth but bars are not great
)

fig.update_layout(
    height=800,
    width=1130,
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    legend=dict(
    orientation="h",
    yanchor="bottom",
    y=0.16,
    xanchor="center",
    x=0.5,
    font=dict(size=10),        # smaller font
    itemwidth=30,              # tighter spacing
    itemsizing="constant",
    bordercolor="lightgrey",
    borderwidth=1)
)  

# Show or save
if save_output:
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, title_plot)
    fig.write_image(output_file, width=1135, height=800, scale=2)
else:
    fig.show()