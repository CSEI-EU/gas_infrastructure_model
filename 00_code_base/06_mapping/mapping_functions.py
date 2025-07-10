# Import useful libraries
import os 
import geopandas as gpd
import pandas as pd
from shapely import wkt
import geopy.distance
from shapely.geometry import Point
from tqdm import tqdm
from datetime import date
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, MultiPoint


# Function to read data  
def read_data(file_name, sheet_name):
    file = pd.read_excel(file_name, sheet_name=sheet_name)
    file_gpd = gpd.GeoDataFrame(file, geometry=gpd.points_from_xy(file.Longitude, file.Latitude),
                                crs='EPSG:4326').to_crs('EPSG:3857')
    return (file_gpd)

# Function for WKT points to clean the data
def tuple_to_wkt_point(s):
    x_str, y_str = s.strip().replace("(", "").replace(")", "").split(",")
    return f"POINT({x_str} {y_str})"


# Function to map demand nd supply to closest nodes 
def AggregatedDemand(df1, df2):
    for index, row1 in tqdm(df1.iterrows(), total=df1.shape[0]):
        for _, row2 in df2.iterrows():
            if row1['ID'] == row2['Closest_node']:
                df1.loc[index, 'Demand'] += row2['Peak Load [MWh/h]']
    return df1

def AggregatedSupply(df1, df2):
    for index, row1 in tqdm(df1.iterrows(), total=df1.shape[0]):
        for _, row2 in df2.iterrows():
            if row1['ID'] == row2['Closest_node']:
                df1.loc[index, 'Supply'] += row2['Peak Load [MWh/h]']
    return df1

def AddStorage(df1, df2, aggregated):
    if sum(df2['Peak Load [MWh/h]']) <= 0:
        df2['Peak Load [MWh/h]'] = df2['Peak Load [MWh/h]'] * (-1)
        aggregated = AggregatedSupply(df1, df2)
    else:
        aggregated = AggregatedDemand(df1, df2)

    return aggregated

def find_closest_location(df1, df2):
    closest_node = []
    closest_distance = []

    for _, row1 in tqdm(df1.iterrows(), total=df1.shape[0]):
        max_distance = float('inf')

        for _, row2 in df2.iterrows():
            coords_1 = (row1['Latitude'], row1['Longitude'])
            coords_2 = (row2['Latitude'], row2['Longitude'])
            distance = geopy.distance.distance(coords_1, coords_2).km
            if distance < max_distance:
                node = row2['ID']
                max_distance = distance

        closest_node.append(node)
        closest_distance.append(max_distance)
    return closest_node, closest_distance

# Function to get the centroids for NUTS3 region
def get_NUT3_centroid(df1, df2):
    shape= pd.DataFrame()
    shape['NUTS3'] = [df2.NUTS_ID.values[i] for i in range(len(df2.index))]
    shape['geometry']= [df2.geometry.values[i] for i in range(len(df2.index))]

    merged_df = pd.merge(df1, shape[['NUTS3', 'geometry']], on = 'NUTS3', how='left')
    merged_gdf = gpd.GeoDataFrame(merged_df, geometry= 'geometry',crs = 'EPSG:4326')
    merged_gdf.to_crs('EPSG:3857', inplace = True)
    merged_gdf.dropna(inplace=True)
    merged_gdf['geometry']= [merged_gdf.geometry.centroid.values[i] for i in range(len(merged_gdf.index))]
    merged_gdf.to_crs('EPSG:4326', inplace = True)

    merged_gdf['Longitude']=merged_gdf.geometry.x
    merged_gdf['Latitude']=merged_gdf.geometry.y
    return(merged_gdf)

# Clean the data and plz file 
def clean_column(df, column_name):
    df[column_name] = (
        df[column_name].astype(str)
        .str.replace(',', '.', regex=False)
        .str.replace(' ', '', regex=False)
    )
    df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
    return df

def clean_plz(series):
    return (
        series.astype(str)
              .str.replace('\u00A0', '', regex=False)  # need to remove breaks or space and have the normal plz format
              .str.replace(' ', '', regex=False)     
              .str.strip()
              .str.zfill(5)  
    )


# In the case of sheets with direct access to latitude and longitude 
def latlon_case(df):
    for col in ['Latitude', 'Longitude', 'Peak Load [MWh/h]']:
        df = clean_column(df, col)

    df = df.dropna(subset=['Latitude', 'Longitude'])
    geometry = gpd.points_from_xy(df['Longitude'], df['Latitude'])
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
    return gdf[['Latitude', 'Longitude', 'Peak Load [MWh/h]', 'geometry']]


# Function to generate Voronoi polygons 
def generate_voronoi_polygons(points):
    vor = Voronoi(points.apply(lambda p: [p.x, p.y]).tolist())

    # Build the polygons
    voronoi_polygons = []
    for i, region_index in enumerate(vor.point_region):
        region = vor.regions[region_index]
        if not region or -1 in region:
            continue
        polygon = Polygon([vor.vertices[i] for i in region])
        voronoi_polygons.append(polygon)

    # Create the GeoDataframe 
    voronoi_df = gpd.GeoDataFrame(geometry=voronoi_polygons, crs="EPSG:4326")
    return voronoi_df