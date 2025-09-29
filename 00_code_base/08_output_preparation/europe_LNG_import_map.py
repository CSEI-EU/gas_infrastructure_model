import os
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import requests
from shapely.geometry import MultiPolygon

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
fix_iso = {"France": "FRA", "Norway": "NOR", "Kosovo": "XKX"}
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
    return "#d8d8d8" if np.any(vals > 0) else "white"

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
# Store all values to find global maximum across all countries and scenarios
all_vals = []
for region_name in excel_countries:
    if region_name in data_gas_prod['Country'].values:
        vals = data_gas_prod.loc[data_gas_prod['Country'] == region_name, scenarios].values.flatten()
        all_vals.extend(np.sqrt(vals))

all_vals = np.array(all_vals)
global_max = all_vals.max()
scale_factor = 25.0 
records =[]

for country in excel_countries:
    vals = data_gas_prod.loc[data_gas_prod["Country"] == country, scenarios].values.flatten()
    vals_sqrt = np.sqrt(vals)
    vals_scaled = vals_sqrt / global_max * scale_factor if global_max != 0 else np.zeros_like(vals_sqrt)

    shp_name = country_name_map.get(country, country)
    geom_row = world_europe[world_europe["NAME"] == shp_name]

    if geom_row.empty:
        print(f"WARNING: No geometry found for {country}")
        continue

    geom = geom_row["geometry"].values[0]
    centroid = get_centroid(geom)
    x, y = centroid.x, centroid.y

    for scenario, v, v_sqrt, v_scaled in zip(scenarios, vals, vals_sqrt, vals_scaled):
        records.append({
            "Region": country,
            "Scenario": scenario,
            "Value": v,
            "Sqrt(Value)": v_sqrt,
            "Scaled Height": v_scaled
        })

    width = 0.3
    bar_positions = np.arange(len(vals)) * width
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
print(df_bars[df_bars["Region"]== "France"])
print(df_bars[df_bars["Region"]== "Spain"])
print(df_bars[df_bars["Region"]== "Ukraine"])


legend_scenarios = [
    Patch(facecolor="#4f81bd", label="2021"),
    Patch(facecolor="#2ca02c", label="2024"),
    Patch(facecolor="#ca2e2e", label="2035 High Demand"),
    Patch(facecolor="#732ca0", label="2035 Low Demand"),
]
ax.legend(handles=legend_scenarios, loc="lower left", title="Bar heights sqrt-normalized", frameon=True)

# Scale inset
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
axins = inset_axes(
    ax, width="2%", height="20%", loc="lower left",
    bbox_to_anchor=(0.20, 0.02, 1, 1),
    bbox_transform=ax.transAxes, borderpad=0
)
axins.bar(0, 25, width=0.6, color="lightgrey", edgecolor="black")
axins.set_ylim(0, 25)
axins.set_xticks([])
axins.set_yticks([0, 25])
axins.set_yticklabels(["0", "max"], fontsize=8)
axins.set_frame_on(False)


ax.set_axis_off()
ax.set_aspect("equal")
plt.tight_layout()
plt.show()


if save_output:
    fig.savefig(output_path + "europe_gas_prod.png", dpi=300)
