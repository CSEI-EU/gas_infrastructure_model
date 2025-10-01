import os
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import requests
from shapely.geometry import MultiPolygon
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# Change parameters for output
save_output = False
scenarios = ["2021", "2024", "2035 High Demand", "2035 Low Demand"]  

# Input data
input_file_path = os.path.join('01_data', '01_input_data', '02_processed', '01_paper_IAEE', '01_data_sheets_input')
input_file = '\\paper_paris_2025_input_production_europe_capacities.xlsx'
full_input_path = os.path.abspath(os.path.join(os.getcwd(), input_file_path + input_file))
data_gas_prod = pd.read_excel(full_input_path)

# Fix commas in Excel
# Convert European-style numbers (comma as decimal) to float
for col in scenarios:
    data_gas_prod[col] = data_gas_prod[col].astype(str).str.replace(",", ".", regex=False).astype(float)

# Add Sweden and Montenegro manually
extra_countries = ["Sweden", "Montenegro"]
for c in extra_countries:
    if c not in data_gas_prod["Country"].values:
        data_gas_prod = pd.concat([
            data_gas_prod,
            pd.DataFrame([{"Country": c, **{s: 0.0 for s in scenarios}}])
        ], ignore_index=True)

excel_countries = [c for c in data_gas_prod["Country"].unique() if c != "Total"]

# Output path
output_path = os.path.join("02_plots")

# World shapefile
shapefile_path = os.path.join('01_data', '01_input_data', '01_raw', 'world_countries_shapefile')
shapefile = '\\ne_50m_admin_0_countries_lakes.shp'
full_shapefile_path = os.path.abspath(os.path.join(os.getcwd(), shapefile_path + shapefile))
world = gpd.read_file(full_shapefile_path)


# Fix Crimea handling (attach to Ukraine instead or Russia)
ukraine_json_url = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_UKR_0.json"
ukraine_json_path = os.path.join("00_code_base", "08_output_preparation", "gadm41_UKR_0.json")
response = requests.get(ukraine_json_url)
with open(ukraine_json_path, "wb") as f:
    f.write(response.content)
ukraine_corrected = gpd.read_file(ukraine_json_path)
ukraine_corrected["NAME"] = "Ukraine"
world = world[world["NAME"] != "Ukraine"]
world = pd.concat([world, ukraine_corrected], ignore_index=True)


# Clean ISO_A3: replace errors with country codes (error for Norway, France and Kosovo)
fix_iso = {"France": "FRA", "Kosovo": "XKX"}
world["ISO_A3"] = world.apply(lambda row: fix_iso.get(row["NAME"], row["ISO_A3"]), axis=1)


country_name_map = {
    "UK": "United Kingdom",
    "Türkiye": "Turkey",
    "Luxemburg": "Luxembourg",
    "Czech Republic": "Czechia",
    "Bosnia and Herzegovina": "Bosnia and Herz.",
    "North Macedonia": "North Macedonia"
}

# Remove Crimea from Russia 
russia_idx = world['ISO_A3'] == "RUS"
ukraine_idx = world['ISO_A3'] == "UKR"
if not world.loc[russia_idx, 'geometry'].empty and not world.loc[ukraine_idx, 'geometry'].empty:
    russia_geom = world.loc[russia_idx, 'geometry'].values[0]
    ukraine_geom = world.loc[ukraine_idx, 'geometry'].values[0]
    world.loc[russia_idx, 'geometry'] = russia_geom.difference(ukraine_geom)


# Change the correct crs 
world = world.to_crs("EPSG:4326")
world_europe = world[world["NAME"].isin([country_name_map.get(c, c) for c in excel_countries])]


def country_color(country):
    vals = data_gas_prod.loc[data_gas_prod["Country"]==country, scenarios].values.flatten()
    return "#b5b4b4" if np.any(vals > 0) else "#DFDFDF"

world_europe["color"] = world_europe["NAME"].apply(lambda n: country_color(
    {v:k for k,v in country_name_map.items()}.get(n, n)
))

# For Spain and France, handling of centroids 
def get_centroid(geom):
    if isinstance(geom, MultiPolygon):
        largest = max(geom.geoms, key=lambda p: p.area)  # Take largest polygon
        return largest.centroid
    else:
        return geom.centroid
    
france_geom = world[world["NAME"] == "France"]
france_geom = france_geom[france_geom.centroid.x.between(-5, 10) & france_geom.centroid.y.between(41, 51)]


# Plot base map
fig, ax = plt.subplots(figsize=(15, 12))
world.plot(ax=ax, color="white", edgecolor="grey", linewidth=0.5, zorder=0)
world_europe.plot(ax=ax, color=world_europe["color"], edgecolor="grey", linewidth=0.6, zorder=1)

# Limit to Europe
ax.set_xlim(-25, 45)
ax.set_ylim(34, 72)

# Bar plots first 
# Store all values to find global max (raw and sqrt)
all_vals_raw = []
all_vals_sqrt = []

for country in excel_countries:
    if country in data_gas_prod['Country'].values:
        vals = data_gas_prod.loc[data_gas_prod['Country'] == country, scenarios].values.flatten()
        all_vals_raw.extend(vals)
        all_vals_sqrt.extend(np.sqrt(vals))

vals_for_scaling = data_gas_prod.loc[data_gas_prod['Country'] != "Total", scenarios].values.flatten()
vals_for_scaling = np.array(vals_for_scaling, dtype=float)

global_max_raw = vals_for_scaling.max()
global_max_sqrt = np.sqrt(global_max_raw)
scale_factor = 0.3
records = []


# Fix some positions 
bar_position_fixed = {
    "Slovakia": (0.6, 0),  
    "Hungary": (-0.6, 0),
    "Norway": (-6, -4),     
}

for country in excel_countries:
    vals = data_gas_prod.loc[data_gas_prod["Country"] == country, scenarios].values.flatten()
    vals_sqrt = np.sqrt(vals)
    vals_scaled = np.sqrt(vals) / np.sqrt(global_max_sqrt) * scale_factor

    shp_name = country_name_map.get(country, country)
    geom_row = world_europe[world_europe["NAME"] == shp_name]

    if geom_row.empty:
        print(f"WARNING: No geometry found for {country}")
        continue

    geom = geom_row["geometry"].values[0]
    centroid = get_centroid(geom)
    x, y = centroid.x, centroid.y
    if country in bar_position_fixed:
        x += bar_position_fixed[country][0]
        y += bar_position_fixed[country][1]


    for scenario, v, v_sqrt, v_scaled in zip(scenarios, vals, vals_sqrt, vals_scaled):
        records.append({
            "Region": country,
            "Scenario": scenario,
            "Value": v,
            "Sqrt(Value)": v_sqrt,
            "Scaled Height": v_scaled
        })

    width = 0.3
    spacing = 1.2
    bar_positions = np.arange(len(vals)) * width * spacing
    ax.bar(
        x + bar_positions - width,
        vals_scaled,
        width=width,
        bottom=y,
        color=["#4f81bd", "#2ca02c", "#ca2e2e", "#732ca0"],
        align='center',
        zorder=5
    )

df_bars = pd.DataFrame(records)
print(df_bars[df_bars["Region"]== "Norway"])


legend_scenarios = [
    Patch(facecolor="#4f81bd", label="2021"),
    Patch(facecolor="#2ca02c", label="2024"),
    Patch(facecolor="#ca2e2e", label="2035 Stated Policies"),
    Patch(facecolor="#732ca0", label="2035 Announced Policies"),
    Patch(facecolor="#b5b4b4", label="Producing European country"),
    Patch(facecolor="#DFDFDF", label="No production"),
]
ax.legend(handles=legend_scenarios, loc="lower left", title="Bar heights sqrt-normalized", frameon=True)

# Scale the bar height 
axins = inset_axes(
    ax, width="2%", height="25%",
    loc="lower left",
    bbox_to_anchor=(0.1, 0.3, 1, 1),  
    bbox_transform=ax.transAxes,
    borderpad=0
)

tick_vals = np.linspace(0, scale_factor, 5)
tick_labels = [f"{int((val / scale_factor * global_max_sqrt)**2)}" for val in tick_vals]


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


if save_output:
    fig.savefig(output_path + "europe_gas_prod.png", dpi=300)
