import os
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import requests


# Change parameters for output 
save_output = False
scenarios = ["2021", "2024", "2035 High Demand"] #, "2035 Low Demand"] 

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
    "Oceania": world[world["CONTINENT"] == "Oceania"]["ISO_A3"].tolist(),
    "South America": world[world["CONTINENT"] == "South America"]["ISO_A3"].tolist(),
    "North America": world[world["CONTINENT"] == "North America"]["ISO_A3"].tolist(),
    "Caspian Region": ["AZE", "KAZ", "UZB", "KGZ", "TKM", "TJK", "GEO"],
    "Middle East": ["SAU", "QAT", "UAE", "KWT", "OMN", "IRQ", "ISR", "JOR", "SYR", "LBN", "YEM", "ARE", "IRN",],
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

asia_exclusions = ["TUR"] + region_to_countries["Middle East"] + region_to_countries["Caspian Region"]
region_to_countries["Asia"] = [
    c for c in world[world["CONTINENT"] == "Asia"]["ISO_A3"].tolist()
    if c not in asia_exclusions
] + ["PNG"]


# Build the map
fig, ax = plt.subplots(figsize=(20, 10))
world.plot(ax=ax, color="white", edgecolor="grey", linewidth=0.5)
world.loc[world["ISO_A3"] == "ERI", "CONTINENT"] = "Africa"

# Regions with data 
regions_with_data = set(data_gas_prod['Country'].unique())
regions_with_data = {r for r in regions_with_data if r != "Total"}

# Define regions for coloring
specific_regions = [
    "Africa", "North America", "South America",
    "Middle East", "Caspian Region", "Asia",
    "Russia", "Australia", "Trinidad & Tobago",
    "Indonesia & Malaysia", "Ukraine", "Oceania", # "USA"
    # "Egypt", "Algeria", "Tunisia", "Libya", "Morroco", "China", "India", "Qatar"
]
pastel_colors = {
    "Africa": "#c7e9c0",
    "North America": "#bae4f5",
    "South America": "#9ecae1",
    "Middle East": "#fdd0a2",
    "Caspian Region": "#fdae6b",
    "Asia": "#fcbba1",
    "Oceania": "#dadaeb",
    "Russia": "#fee6ce",
    "Australia": "#dadaeb",
    "Trinidad & Tobago": "#e0f3db",
    "Indonesia & Malaysia": "#f8a788",
    "Ukraine": "#fcbf91"
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

vals_for_scaling = data_gas_prod.loc[data_gas_prod['Country'] != "Total", scenarios].values.flatten()
vals_for_scaling = np.array(vals_for_scaling, dtype=float)

global_max_raw = vals_for_scaling.max()
global_max_sqrt = np.sqrt(global_max_raw)  
scale_factor = 25.0

# Fix the position of some bars
bar_position_fixed = {
    "North America": (-98.5, 39.8),  # central USA for North America 
    "Middle East": (41.50, 27.6),  # move bars when Qatar appears 
}

records = []
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

    for scenario, v, v_sqrt, v_scaled in zip(scenarios, vals, vals_sqrt, vals_scaled):
        records.append({
            "Region": region_name,
            "Scenario": scenario,
            "Value": v,
            "Sqrt(Value)": v_sqrt,
            "Scaled Height": v_scaled
        })

    width = 1.2
    bar_positions = np.arange(len(vals)) * width
    ax.bar(
        x + bar_positions - width*1.5,
        vals_scaled,
        width=0.97,
        bottom=y,
        #color=['#1f77b4','#ff7f0e','#d62728'], #,'#2ca02c'],
        color= ["#4f81bd", "#2ca02c", "#ca2e2e"], #,'#2ca02c'],
        align='center',
        zorder=5
    )

df_bars = pd.DataFrame(records)
#print(df_bars)

# Highlighted countries
highlight_countries = {
    "USA": "#62a7d7",       
    "BLR": "#fee6ce",      
    "QAT": "#e6550d",  
    "DZA": "#5fa179",       
    "EGY": "#5fa179",       
    "MAR": "#5fa179",       
    "LBY": "#5fa179",       
    "TUN": "#5fa179",    
    "NZL": "#dadaeb",
    "MYS": "#eb916d", 
    "IND": "#f48e65", 
    "CHN": "#ee9073", 
    "HKG": "#ee9073",
    "KOR": "#dd7762", 
    "JPN": "#dd7762",
}

# Plot countries used in model
for iso_code, color in highlight_countries.items():
    highlight_geom = world[world["ISO_A3"] == iso_code]
    if not highlight_geom.empty:
        highlight_geom.plot(ax=ax, color=color, edgecolor="grey", linewidth=0.5, zorder=2)



# Create two legends, one for bar colors and one for bar heights
from matplotlib.patches import Patch
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# Scenario colors 
legend_scenarios = [
    Patch(facecolor="#4f81bd", label="2021"),
    Patch(facecolor="#2ca02c", label="2024"),
    Patch(facecolor="#ca2e2e", label="2035"),
]

# Region with all different colors 
light_colors = {
    "Africa": "#c7e9c0",
    "North America": "#bae4f5",
    "South America": "#9ecae1",
    "Middle East": "#fdd0a2",
    "Asia": "#fcbba1",
    "India": "#f48e65", 
    "Oceania": "#dadaeb",  
    "Russia": "#fee6ce",
}

dark_colors = {
    "Africa": "#5fa179",     
    "America": "#62a7d7",   
    "Middle East": "#e6550d",
    "Caspian Region": "#fdae6b",
    "Asia": "#ee9073",
}

dark_labels = {
    "Africa": "North Africa",
    "America": "USA",
    "Middle East": "Qatar",
    "Asia": "Asia modelled countries"
}


# Combine all legends 
region_handles = []
for region in light_colors.keys():
    region_handles.append(Patch(facecolor=light_colors[region], edgecolor="grey", label=region))
    if region in dark_colors:
        region_handles.append(Patch(facecolor=dark_colors[region], edgecolor="grey", label=dark_labels[region]))

# Merge with scenarios
all_handles = legend_scenarios + region_handles
leg = ax.legend(
    handles=all_handles,
    loc="lower left",
    bbox_to_anchor=(0.0, -0.05),
    ncol=2,
    frameon=True,
    title="Legend: Regions are modelled as a single node for the bright parts"
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
        return f"{round(val/1_000_000,1)}M"   # 1.2M
    elif val >= 1_000:
        return f"{round(val/1_000)}k"         # 500k
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
    fig.savefig(output_path + "_map_bars.png", dpi=300)