import os 
import geopandas as gpd
import pandas as pd 
import plotly.express as px
import numpy as np
import base64, io

# Call input file and create dataframe
input_file_path = os.path.join('01_data', '01_input_data', '02_processed', '01_paper_IAEE', '01_data_sheets_input')
input_file = '\\paper_paris_2025_input_production_world.xlsx'  
full_input_path = os.path.abspath(os.path.join(os.getcwd(), input_file_path + input_file))
data_gas_prod = pd.read_excel(full_input_path)

# Convert to dot and float 
for col in data_gas_prod.columns[1:]:
    data_gas_prod[col] = data_gas_prod[col].astype(str).str.replace(",", ".").astype(float)
# print(data_gas_prod.head())

region_to_countries = {
    "Africa": ["EGY","LBA","TUN","ZAF"],  # list of countries in Africa
    "Algeria": ["DZA"],
    "Asia": ["CHN","IND","JPN","KOR"],           # only major countries
    "Australia": ["AUS"],
    "Caspian Region": ["AZE","KAZ","TUR","IRN","RUS"],
    "China": ["CHN"],
    "Egypt": ["EGY"],
    "India": ["IND"],
    "Indonesia & Malaysia": ["IDN","MYS"],
    "Japan & South Korea": ["JPN","KOR"],
    "Libya": ["LBA"],
    "Middle East": ["SAU","QAT","UAE","KWT","OMN","IRQ","ISR","JOR","SYR","LBN"],
    "Morocco": ["MAR"],
    "North America": ["USA","CAN","MEX"],
    "Qatar": ["QAT"],
    "Russia": ["RUS"],
    "South America": ["BRA","ARG","CHL","COL","PER"],
    "Trinidad & Tobago": ["TTO"],
    "Tunisia": ["TUN"],
    "USA": ["USA"]
}

scenarios = ["2021","2024","2035 High Demand","2035 Low Demand"]

# create an encocded image of graph...
# change to generate graph you want
def b64image(row):
    vals = row[scenarios].values
    df_bar = pd.DataFrame({"scenario": scenarios, "value": vals})

    fig = px.bar(
        df_bar,
        x="scenario",
        y="value",
        color="scenario",
        orientation="v"
    ).update_layout(
        showlegend=False,
        xaxis_visible=False,
        yaxis_visible=False,
        bargap=0.1,
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        autosize=False,
        height=200,
        width=80,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    b = io.BytesIO(fig.to_image(format="png"))
    b64 = base64.b64encode(b.getvalue())
    return "data:image/png;base64," + b64.decode("utf-8")




# get some geometry
world = gpd.read_file("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson")
# print(world.head())

# Prepare mapbox_layers
mapbox_layers = []

for i, row in data_gas_prod.iterrows():
    region_name = row['Country']
    if region_name not in region_to_countries:
        continue 

    countries = region_to_countries[region_name]
    region_geom = world[world['ISO_A3'].isin(countries)]['geometry'].unary_union
    if region_geom.is_empty:
        continue
    cent = region_geom.centroid

    b64 = b64image(row)

    size_x = 2.0
    size_y = 5.0
    coords = [
        [cent.x-size_x, cent.y-size_y],
        [cent.x-size_x, cent.y+size_y],
        [cent.x+size_x, cent.y+size_y],
        [cent.x+size_x, cent.y-size_y]
    ]

    mapbox_layers.append({
        "sourcetype":"image",
        "source":b64,
        "coordinates": coords
    })


# Create a dict mapping ISO_A3 to value
country_values = {}
for region, countries in region_to_countries.items():
    if region in data_gas_prod['Country'].values:
        value = data_gas_prod.loc[data_gas_prod['Country'] == region, scenarios[-1]].values[0]
        for c in countries:
            country_values[c] = value

world['value'] = world['ISO_A3'].map(country_values)
world['has_value'] = world['ISO_A3'].isin(country_values)
world['color'] = world['has_value'].map({True: "lightgrey", False: "white"})


fig = px.choropleth_mapbox(
    world,
    geojson=world.__geo_interface__,
    locations='ISO_A3',
    featureidkey='properties.ISO_A3',
    color="color",
    color_discrete_map={"lightgrey":"lightgrey","white":"white"}
)

fig.update_layout(
    margin={"l":0,"r":0,"t":0,"b":0},
    mapbox_style="carto-positron",
    mapbox_zoom=1,
    mapbox_center={"lon": world.union_all().centroid.x,
                   "lat": world.union_all().centroid.y},
    mapbox_layers=mapbox_layers
)

fig.show()