import os
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import requests

# Change parameters for output 
save_output = False
scenarios = ["2021", "2024", "2035 High Demand", "2035 Low Demand"] 

# Input data
input_file_path = os.path.join('01_data', '01_input_data', '02_processed', '01_paper_IAEE', '01_data_sheets_input')
input_file = '\\paper_paris_2025_input_production_world.xlsx'
full_input_path = os.path.abspath(os.path.join(os.getcwd(), input_file_path + input_file))
data_gas_prod = pd.read_excel(full_input_path)

# Output path
output_path = os.path.join('02_plots')

# World shapefile
shapefile_path = os.path.join('01_data', '01_input_data', '01_raw', 'world_countries_shapefile')
shapefile = '\\ne_50m_admin_0_countries_lakes.shp'
full_shapefile_path = os.path.abspath(os.path.join(os.getcwd(), shapefile_path + shapefile))


# Fix Crimea handling (attach to Ukraine instead or Russia)
ukraine_json_url = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_UKR_0.json"
ukraine_json_path = os.path.join("00_code_base", "08_output_preparation", "gadm41_UKR_0.json")
response = requests.get(ukraine_json_url)
with open(ukraine_json_path, "wb") as f:
    f.write(response.content)
ukraine_corrected = gpd.read_file(ukraine_json_path)


# Concatenate world shapefile with the corrected Ukraine
world = gpd.read_file(full_shapefile_path)
world = world[world["NAME"] != "Ukraine"]  # remove old Ukraine
ukraine_corrected = ukraine_corrected.rename(columns={"GID_0":"ISO_A3", "NAME_0":"NAME"})
world = pd.concat([world, ukraine_corrected], ignore_index=True)


# Clean ISO_A3: replace errors with country codes (error for Norway, France and Kosovo)
fix_iso = {"France": "FRA", "Norway": "NOR", "Kosovo": "XKX"}
world["ISO_A3"] = world.apply(
    lambda row: fix_iso.get(row["NAME"], row["ISO_A3"]),
    axis=1
)

# Remove Antarctica
world = world[world["CONTINENT"] != "Antarctica"]

# Remove Crimea from Russia geometry
russia_idx = world['ISO_A3'] == "RUS"
ukraine_idx = world['ISO_A3'] == "UKR"

if not world.loc[russia_idx, 'geometry'].empty and not world.loc[ukraine_idx, 'geometry'].empty:
    russia_geom = world.loc[russia_idx, 'geometry'].values[0]
    ukraine_geom = world.loc[ukraine_idx, 'geometry'].values[0]
    world.loc[russia_idx, 'geometry'] = russia_geom.difference(ukraine_geom)

# Region-to-countries mapping
region_to_countries = {
    "Africa": world[world["CONTINENT"] == "Africa"]["ISO_A3"].tolist(),
    "Asia": world[world["CONTINENT"] == "Asia"]["ISO_A3"].tolist(),
    "South America": world[world["CONTINENT"] == "South America"]["ISO_A3"].tolist(),
    "North America": world[world["CONTINENT"] == "North America"]["ISO_A3"].tolist(),
    "Caspian Region": ["AZE", "KAZ", "TUR", "IRN"],
    "Middle East": ["SAU", "QAT", "UAE", "KWT", "OMN", "IRQ", "ISR", "JOR", "SYR", "LBN"],
    "Indonesia & Malaysia": ["IDN", "MYS"],
    "Japan & South Korea": ["JPN", "KOR"],
    "Algeria": ["DZA"],
    "China": ["CHN"],
    "Egypt": ["EGY"],
    "India": ["IND"],
    "Libya": ["LBA"],
    "Morroco": ["MAR"], # typo in the excel 
    "Qatar": ["QAT"],
    "Russia": ["RUS"],
    "Trinidad & Tobago": ["TTO"],
    "Tunisia": ["TUN"],
    "USA": ["USA"],
    "Australia": ["AUS"],
    "Ukraine": ["UKR"]
}


# Build the map
fig, ax = plt.subplots(figsize=(20, 10))
world.plot(ax=ax, color="white", edgecolor="grey", linewidth=0.5)

# Regions with data 
regions_with_data = set(data_gas_prod['Country'].unique())
regions_with_data = {r for r in regions_with_data if r != "Total"}

# Define regions for coloring
specific_regions = [
    "Africa", "North America", "South America",
    "Middle East", "Caspian Region", "Asia",
    "Russia", "Australia", "Trinidad & Tobago",
    "Indonesia & Malaysia", "Ukraine"
]
pastel_colors = {
    "Africa": "#c7e9c0",
    "North America": "#bae4f5",
    "South America": "#9ecae1",
    "Middle East": "#fdd0a2",
    "Caspian Region": "#fdae6b",
    "Asia": "#fcbba1",
    "Russia": "#fee6ce",
    "Australia": "#dadaeb",
    "Trinidad & Tobago": "#e0f3db",
    "Indonesia & Malaysia": "#f2f0f7",
    "Ukraine": "#fcbf91"
}

# Plot all specific regions with colors 
# Caspian first
caspian_countries = region_to_countries["Caspian Region"]
world_plot = world[world['ISO_A3'].isin(caspian_countries)]
world_plot.plot(ax=ax, color=pastel_colors["Caspian Region"], edgecolor="grey", linewidth=0.5, zorder=1)

# Other regions, without the Caspian
for region_name in specific_regions:
    if region_name == "Caspian Region":
        continue
    if region_name in regions_with_data:
        countries = [c for c in region_to_countries[region_name] if c not in caspian_countries]
        world_plot = world[world['ISO_A3'].isin(countries)]
        if not world_plot.empty:
            color = pastel_colors.get(region_name, "#cccccc")
            world_plot.plot(ax=ax, color=color, edgecolor="grey", linewidth=0.5, zorder=1)



# Plot bars over regions 
for region_name in specific_regions:
    if region_name not in region_to_countries:
        continue

    countries = region_to_countries[region_name]
    region_geom = world[world['ISO_A3'].isin(countries)]['geometry'].union_all()
    if region_geom.is_empty:
        continue

    x, y = region_geom.centroid.x, region_geom.centroid.y
    if region_name in data_gas_prod['Country'].values:
        vals = data_gas_prod.loc[data_gas_prod['Country'] == region_name, scenarios].values.flatten()
    else:
        vals = np.zeros(len(scenarios))


    # Log scale without target height
    vals_scaled = np.log1p(vals)
    
    '''
    # Log scale for bars 
    vals_log = np.log1p(vals)
    max_val = vals_log.max()
    target_height = 10.0
    scale_factor = target_height / max_val if max_val > 0 else 1
    vals_scaled = vals_log * scale_factor


    # Target height and scaling 
    max_val = vals.max()
    target_height = 10.0
    scale_factor = target_height / max_val if max_val > 0 else 1
    vals_scaled = vals * scale_factor'''

    width = 1.0
    bar_positions = np.arange(len(vals)) * width
    ax.bar(
        x + bar_positions - width*1.5,
        vals_scaled,
        width=0.9,
        bottom=y,
        color=['#1f77b4','#ff7f0e','#d62728','#2ca02c'],
        align='center',
        zorder=5
    )

# Legend for bars
legend_elements = [
    Patch(facecolor='#1f77b4', label='2021'),
    Patch(facecolor='#ff7f0e', label='2024'),
    Patch(facecolor='#d62728', label='2035 High Demand'),
    Patch(facecolor='#2ca02c', label='2035 Low Demand'),
]
ax.legend(handles=legend_elements, loc='lower left')

ax.set_axis_off()
ax.set_aspect('equal')
plt.tight_layout()
plt.show()

if save_output: 
    fig.savefig(output_path + "_map_bars.png", dpi=300)
