import os
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import requests
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# Change parameters for output 
save_output = False
scenarios = ["2021", "2024", "2035 High Demand"] #, "2035 Low Demand"] 

# Input data
input_file_path = os.path.join('01_data', '01_input_data', '02_processed', '01_paper_IAEE', '01_data_sheets_input')
input_file = '\\paper_paris_2025_input_production_world.xlsx'
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
world["ISO_A3"] = world.apply(lambda row: fix_iso.get(row["NAME"], row["ISO_A3"]),axis=1)

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
    "Oceania": world[world["CONTINENT"] == "Oceania"]["ISO_A3"].tolist(),
    "Australia": ["AUS", "NZL"],  # Combined Australia + New Zealand
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

# Build the map
fig, ax = plt.subplots(figsize=(20, 10))
world.plot(ax=ax, color="white", edgecolor="grey", linewidth=0.5)
world.loc[world["ISO_A3"] == "ERI", "CONTINENT"] = "Africa"

# Regions with data in the excel
regions_with_data = set(data_gas_prod['Country'].unique())
regions_with_data = {r for r in regions_with_data if r != "Total"}

# Define regions for coloring
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

# Highlighted countries
highlight_countries = {
    "USA": "#2e8ccf",
    #"NZL": pastel_colors["Australia"], 
    "TTO": "#2e3bcf",     
    "QAT": "#e6550d",  
    "DZA": "#247143",       
    "EGY": "#247143",       
    "MAR": "#247143",       
    "LBY": "#247143",       
    "TUN": "#247143",
    "MYS": "#e36c3d", 
    "IND": "#e36c3d", 
    "CHN": "#e36c3d", 
    "IDN": "#e36c3d", 
    "HKG": "#e36c3d",
    "KOR": "#dd7762", 
    "JPN": "#dd7762",
}

# Plot all specific regions with colors 
# Caspian first
caspian_countries = region_to_countries["Caspian Region"]
world_plot = world[world['ISO_A3'].isin(caspian_countries)]
world_plot.plot(ax=ax, color=pastel_colors["Caspian Region"], edgecolor="grey", linewidth=0.5, zorder=1)

for region_name in specific_regions:
    if region_name == "Caspian Region":
        continue
    if region_name in regions_with_data:
        countries = [c for c in region_to_countries[region_name] if c not in caspian_countries]
        world_plot = world[world['ISO_A3'].isin(countries)]
        if not world_plot.empty:
            color = pastel_colors.get(region_name, "#cccccc")
            world_plot.plot(ax=ax, color=color, edgecolor="grey", linewidth=0.5, zorder=1)

eri = world[(world["ISO_A3"] == "SOM") | (world["NAME"].str.contains("Soma", na=False))]
if not eri.empty:
    eri.plot(
        ax=ax,
        color=pastel_colors.get("Africa", "#c7e9c0"),  
        edgecolor="grey",
        linewidth=0.5,
        zorder=3   # zorder < bars so bars are on top
    )

# Store all values to find global max (raw and sqrt)
all_vals_raw = []
all_vals_sqrt = []

for region_name in specific_regions:
    if region_name in data_gas_prod['Country'].values:
        vals = data_gas_prod.loc[data_gas_prod['Country'] == region_name, scenarios].values.flatten()
        all_vals_raw.extend(vals)
        all_vals_sqrt.extend(np.sqrt(vals))

# Outline highlighted countries with slightly bigger lines
for iso_code, color in highlight_countries.items():
    geom = world[world["ISO_A3"] == iso_code]
    if not geom.empty:
        geom.boundary.plot(ax=ax, color=color, linewidth=1.2, zorder=3)

# Add LNG port locations
ax.scatter(
    ports_df['Longitude'],
    ports_df['Latitude'],
    color='black',
    s=10,
    marker='o',
    edgecolor='black',
    zorder=6,
    label='LNG Ports'
)

vals_for_scaling = data_gas_prod.loc[data_gas_prod['Country'] != "Total", scenarios].values.flatten()
vals_for_scaling = np.array(vals_for_scaling, dtype=float)

global_max_raw = vals_for_scaling.max()
global_max_sqrt = np.sqrt(global_max_raw)  
scale_factor = 25.0

# Fix the position of some bars
bar_position_fixed = {
    "North America": (-98.5, 39.8),   
    "Middle East": (41.50, 27.6),  # move bars when Qatar appears 
}

for region_name in specific_regions:
    if region_name not in region_to_countries:
        continue

    countries = region_to_countries[region_name]
    region_geom = world[world['ISO_A3'].isin(countries)]['geometry'].union_all()
    if region_geom.is_empty:
        continue

    if region_name in bar_position_fixed:
        x, y = bar_position_fixed[region_name]
    else:
        x, y = region_geom.centroid.x, region_geom.centroid.y

    if region_name in data_gas_prod['Country'].values:
        vals = data_gas_prod.loc[data_gas_prod['Country'] == region_name, scenarios].values.flatten()
    else:
        vals = np.zeros(len(scenarios))

    vals_sqrt = np.sqrt(vals)
    vals_scaled = vals_sqrt / global_max_sqrt * scale_factor

    width = 1.2
    bar_positions = np.arange(len(vals)) * width
    ax.bar(
        x + bar_positions - width*1.5,
        vals_scaled,
        width=0.97,
        bottom=y,
        color= ["#4f81bd", "#2ca02c", "#ca2e2e"],
        align='center',
        zorder=5
    )

# Create two legends, one for bar colors and one for bar heights
legend_scenarios = [
    Patch(facecolor="#4f81bd", label="2021"),
    Patch(facecolor="#2ca02c", label="2024"),
    Patch(facecolor="#ca2e2e", label="2035"),
]

# Add Oceania label especially 
legend_regions = []
for r in specific_regions:
    label = r
    if r == "Australia":  
        label = "Oceania"
    legend_regions.append(Patch(facecolor=pastel_colors[r], edgecolor="grey", label=label))

# Fix LNG legend on the map
from matplotlib.lines import Line2D
legend_ports = [Line2D([0], [0], marker='o', color='w', label='LNG Ports',
                        markerfacecolor='black', markersize=6)]
all_handles = legend_scenarios + legend_regions + legend_ports

leg = ax.legend(
    handles=all_handles,
    loc="lower left",
    bbox_to_anchor=(0.0, -0.15),
    ncol=2,
    frameon=True,
    title="Legend: Regions are modelled as a single node for the outlined parts"
)
ax.add_artist(leg)

# Scale the bar height 
axins = inset_axes(
    ax, width="2%", height="25%",
    loc="lower left",
    bbox_to_anchor=(0.1, 0.2, 1, 1),  
    bbox_transform=ax.transAxes,
    borderpad=0
)

tick_vals = np.linspace(0, scale_factor, 5)

def human_readable(val):
    if val >= 1_000_000:
        return f"{round(val/1_000_000,1)}M"
    elif val >= 1_000:
        return f"{round(val/1_000)}k"
    else:
        return str(int(val))

tick_labels = [
    human_readable((val / scale_factor) * global_max_raw)
    for val in tick_vals
]

axins.bar(0, scale_factor, width=0.6, color="lightgrey", edgecolor="black")
axins.set_ylim(0, scale_factor)
axins.set_xticks([])
axins.set_yticks(tick_vals)
axins.set_yticklabels(tick_labels, fontsize=8)
axins.set_title("GWh/a", fontsize=9)
axins.set_frame_on(False)

ax.set_axis_off()
ax.set_aspect('equal')
plt.tight_layout()
plt.show()

# Save output
if save_output:
    os.makedirs(output_path, exist_ok=True)
    fig.savefig(os.path.join(output_path, "world_map_bar.png"), dpi=300)
