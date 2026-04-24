# import packages
import pandas as pd
import os
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pycountry
import numpy as np

import json 

# Separate the Edge column to have which countries is source and which is destination 
def parse_edges(df):
    df = df.copy()
    
    # Split the edges into source and target
    df['Edge'] = df['Edge'].str.strip('()"')  # remove quotes and parentheses
    df[['From', 'To']] = df['Edge'].str.split(', ', expand=True)

    # Remove extra quotes
    df['From'] = df['From'].str.replace("'", "").str.strip()
    df['To'] = df['To'].str.replace("'", "").str.strip()
    
    return df

# Differentiate each type of edges
def label_node_type(label):
    if '_LNG_exp' in label:
        return 'LNG_export'
    elif '_LNG_imp' in label:
        return 'LNG_import'
    elif '_Prod' in label:
        return 'prod'
    else:
        return '-'
    

# Extract only the country code 
def extract_country_code(label):
    if '_' in label:
        return label.split('_')[0]  # "USA_LNG_exp" just takes the "USA"
    else:
        return label
    
    
# Define the list of countries we want in the map, separate source and destination countries 
#@mathilde: We have to change GR to EL as the model uses the EU country code
#and I ask myself: why there are two lists, they seem to be the same. 
def interesting_countries(code):
    return code in [
        'AL', 'AD', 'AM', 'AT', 'AZ', 'BY', 'BE', 'BA', 'BG', 'CH', 'CR' , 'CY', 'CZ',
        'DE', 'DK', 'DZ', 'EE', 'ES', 'FI', 'FR', 'UK', 'GE', 'EL', 'HR', 'HU', 'IE',
        'IS', 'IT', 'KZ', 'LI', 'LT', 'LU', 'LY', 'LV', 'MA','MC', 'MD', 'ME', 'MK', 'MT',
        'NL', 'NO', 'PL', 'PT', 'RO', 'RS', 'RU', 'SD', 'SE', 'SI', 'SK', 'SM', 'SU', 'TN', 'TR',
        'UA', 'VA', 'XK'
    ]

def european_countries(code):
    return code in [
        'AL', 'AD', 'AM', 'AT', 'AZ', 'BY', 'BE', 'BA', 'BG', 'CH', 'CY', 'CZ',
        'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'UK', 'GE', 'EL', 'HR', 'HU', 'IE',
        'IS', 'IT', 'LI', 'LT', 'LU', 'LV', 'MC', 'MD', 'ME', 'MK', 'MT',
        'NL', 'NO', 'PL', 'PT', 'RO', 'RS', 'SE', 'SI', 'SK', 'SM', 'TR',
        'UA', 'VA', 'XK'
    ]

def eu_countries(code):
    return code in [
        'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
        'DE', 'EL', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
        'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'
    ]


# Calculate the final capacity with and without investment 
def add_capacity_column(df, file_path):
    df = df.copy()
    file_name = os.path.basename(file_path)

    # When there is no investment, we only look at normal capacity
    if "inv" in file_name:
        df['Capacity_tot'] = df['Changed Capacity'].fillna(0) + df['New Capacity'].fillna(0)
    else:
        df['Capacity_tot'] = df['Changed Capacity']
    return df


# Then calulate the share column and add a column to the dataframe 
def add_share_column(df):
    df = df.copy()

    # Function to calculate the share
    def calculate_share(row):
        flow = row['Flow']
        capacity = row['Capacity_tot']
        return flow / capacity if capacity and capacity != 0 else 0

    df['Share'] = df.apply(calculate_share, axis=1)
    return df


# Function to read locations of port according to year
def filter_lng_ports_by_year(file_path, years):
    lng_ports = pd.read_excel(file_path)
    lng_ports_filtered = lng_ports[lng_ports['Model Year'].isin(years)]
    
    return lng_ports_filtered

# Manually write the country coordinates
COUNTRY_COORDINATES = {
    'AL': (41.1533, 20.1683),
    'AD': (42.5462, 1.6016),
    'AM': (40.0691, 45.0382),
    'AT': (47.5162, 14.5501),
    'AZ': (40.1431, 47.5769),
    'BY': (53.7098, 27.9534),
    'BE': (50.8503, 4.3517),
    'BA': (43.9159, 17.6791),
    'BG': (42.7339, 25.4858),
    'CH': (46.8182, 8.2275),
    'CR': (39.3764, 59.3925),
    'CY': (35.1264, 33.4299),
    'CZ': (49.8175, 15.4730),
    'DE': (51.1657, 10.4515),
    'DK': (56.2639, 9.5018),
    'DZ': (28.0339, 1.6596),
    'EE': (58.5953, 25.0136),
    'ES': (40.4637, -3.7492),
    'FI': (61.9241, 25.7482),
    'FR': (46.6034, 1.8883),
    'UK': (51.0, -1.5),  
    'GE': (42.3154, 43.3569),
    'EL': (39.0742, 21.8243),  
    'HR': (45.1, 15.2),
    'HU': (47.1625, 19.5033),
    'IE': (53.1424, -7.6921),
    'IS': (64.9631, -19.0208),
    'IT': (41.8719, 12.5674),
    'KZ': (48.0196, 66.9237),
    'LI': (47.1660, 9.5554),
    'LT': (55.1694, 23.8813),
    'LU': (49.8153, 6.1296),
    'LV': (56.8796, 24.6032),
    'MA': (31.7917, -7.0926),
    'MC': (43.7333, 7.4167),
    'MD': (47.4116, 28.3699),
    'ME': (42.7087, 19.3744),
    'MK': (41.9981, 21.4254),
    'MT': (35.9375, 14.3754),
    'NL': (52.1326, 5.2913),
    'NO': (60.4720, 6.7),
    'PL': (51.9194, 19.1451),
    'PT': (39.3999, -8.2245),
    'RO': (45.9432, 24.9668),
    'RS': (44.0165, 21.0059),
    'RU': (55.0, 40.0),  
    'SD': (12.8628, 30.2176),  
    'SE': (58, 14.5),
    'SI': (46.1512, 14.9955),
    'SK': (48.6690, 19.6990),
    'SM': (43.9333, 12.4500),
    'SU': (55.0, 38.0),
    'TN': (33.8869, 9.5375),  
    'TR': (39.0, 35.0),
    'UA': (48.3794, 31.1656),
    'VA': (41.9029, 12.4534),
    'XK': (42.6026, 20.9020),
    'LY': (26.3351, 17.2283),
}

def get_country_coordinates(country_code):
    return COUNTRY_COORDINATES.get(country_code, (None, None))

# Then add the coordinates to the dataframe for the plot
def add_coordinates(df):
    df = df.copy()

    countries = set(df['From'].tolist() + df['To'].tolist())
    coord_map = {}

    for code in countries:
        lat, lon = get_country_coordinates(code)
        coord_map[code] = {'lat': lat, 'lon': lon}

    df['Source_lat'] = df['From'].apply(lambda x: coord_map[x]['lat'])
    df['Source_lon'] = df['From'].apply(lambda x: coord_map[x]['lon'])
    df['Target_lat'] = df['To'].apply(lambda x: coord_map[x]['lat'])
    df['Target_lon'] = df['To'].apply(lambda x: coord_map[x]['lon'])

    return df

# Put all processing into a single function 
def process_file(file):
    df = pd.read_excel(file)
    df = df[df['Commodity'] == 'Methane']
    df = parse_edges(df)
    df['FromType'] = df['From'].apply(label_node_type)
    df['ToType'] = df['To'].apply(label_node_type)
    df['From'] = df['From'].apply(extract_country_code)
    df['To'] = df['To'].apply(extract_country_code)
    df = df[df['From'].apply(interesting_countries) & df['To'].apply(european_countries)]
    df_capacity = add_capacity_column(df, file)
    df_with_share = add_share_column(df_capacity)

    df_final = add_coordinates(df_with_share)
    df_final['Edge'] = df_final.apply(lambda row: f"{row['From'].strip()}, {row['To'].strip()}", axis=1)
    return df_final


# Points for the LNG import per country 
LNG_IMPORT_COORDS = {
    'BE': (50.3, 4.4),
    'HR': (43.8, 16.0),
    'FI': (63.0, 26.0),
    'FR': (45.5, 2.3),
    'DE': (52.0, 11.0),
    'EL': (38.5, 21.5),
    'IT': (42.5, 13.5),
    'IE': (52.5, -7.6921),
    'LT': (55.8, 23.7),
    'NL': (52.4, 6.0),
    'PL': (51, 21),
    'PT': (40.0, -8.0),
    'ES': (40, -1.8),
    'UK': (52.6, -2.5),
    # 'NO': (61.0, 8.0),
    'EE': (58.6, 26.0),  
    'TR': (38.0, 32.0)
}


# Only keep the countries that appear for the specific year(s)
def get_countries_with_terminals(filtered_ports):
    return set(filtered_ports['Country'].unique())

manual_country_mapping = {
    'United Kingdom': 'UK',
    'Greece': 'EL',
    'Turkey': 'TR',
}

def country_name_to_code(name):
    # First replace manually the ones not working
    if name in manual_country_mapping:
        return manual_country_mapping[name]

    try:
        iso2 = pycountry.countries.lookup(name).alpha_2
        return iso2
    except LookupError:
        return None


def get_corresponding_scenario(filename):
    if "outputs_IAEE_2025_run_2024_plus_NO_reduced" in filename:
        return "2024_NOR"
    elif "outputs_IAEE_2025_run_2024_plus_no_USA" in filename:
        return "2024_USA"
    elif "outputs_IAEE_2025_run_2024_plus_no_QA" in filename:
        return "2024_QA"
    elif "outputs_IAEE_2025_run_2024_with_RU" in filename:
        return "2024_wRU"

    elif "outputs_IAEE_2025_run_2024_inv" in filename:
        return "2024_InvesPipes"
    elif "outputs_IAEE_2025_run_2024" in filename:
        return "2024"
    
    elif "outputs_IAEE_2025_run_2035_AP" in filename:
        return "2035"
    elif "outputs_IAEE_2025_run_2035_SP" in filename:
        return "2035"

    else:
        return None

def excluded_pipelines(file_path, sheet_name):
    if sheet_name is None:
        return None

    df_excluded = pd.read_excel(file_path, sheet_name)
    df_excluded = df_excluded[df_excluded['Commodity'].str.lower() == 'methane']
    df_excluded = df_excluded[['Source', 'Destination']].rename(columns={'Source': 'From', 'Destination': 'To'})
    return df_excluded


# To process pipelines with Russia and excluded ones 
def process_pipelines(df, file_name, input_excluded_pipelines):
    scenario_sheet = get_corresponding_scenario(file_name)
    scenarios_with_exclusion = ["2024_NOR", "2024_USA", "2024_QA", "2024_wRU", "2024_InvesPipes", "2024", "2035"]

    if scenario_sheet in scenarios_with_exclusion:
        excluded_df = excluded_pipelines(input_excluded_pipelines, scenario_sheet)
        
        if excluded_df is not None:
            # Merge to identify excluded pipelines but keep them in the DataFrame
            df_final = df.merge(excluded_df, on=['From', 'To'], how='left', indicator=True)
            df_final['Excluded'] = df_final['_merge'] == 'both'
            df_final = df_final.drop(columns=['_merge'])
        else:
            df_final = df
            df_final['Excluded'] = False
    else:
        df_final = df
        df_final['Excluded'] = False

    return df_final


# Color code for pipelines and LNG shares 
def flow_color(share):
    if share <= 0.0:
        return 'rgba(0, 160, 0, 0.8)'  # Soft green
    elif share >= 1.0:
        return 'rgba(220, 50, 50, 0.8)'  # Soft red 

    if share < 0.5:
        # Green to Orange
        ratio = share / 0.5
        r = int(0 + (255 - 0) * ratio)
        g = int(160 + (165 - 160) * ratio)
        b = int(0 + (0 - 0) * ratio)
    else:
        # Orange to Red
        ratio = (share - 0.5) / 0.5
        r = int(255 + (220 - 255) * ratio)
        g = int(165 + (50 - 165) * ratio)
        b = 0

    return f'rgba({r}, {g}, {b}, 0.8)'


# Final plot of the map
def plot_flow_map(df, ports, imports, lng_import_coords):
    fig = go.Figure()
 
    # First plot the pipeline flows
    df_pipelines = df[(df['FromType'] == '-') & (df['ToType'] == '-')]
 
    for _, row in df_pipelines.iterrows():
        line_color = 'gray' if row.get('Excluded', False) else flow_color(row['Share'])
        line_width = max(row['Capacity_tot'] / 100000, 1.1) if row['Flow'] > 0 else 1

        start_lon = row['Source_lon']
        start_lat = row['Source_lat']
        end_lon = row['Target_lon']
        end_lat = row['Target_lat']
        edge = row.get("Edge", "")

        if ('RU' in edge or 'Russia' in edge) and ('DE' in edge or 'Germany' in edge):
            mid_lon = (start_lon + end_lon) / 2
            mid_lat = max(start_lat, end_lat) + 5

            lons = [start_lon, mid_lon, end_lon]
            lats = [start_lat, mid_lat, end_lat]
        else:
            lons = [start_lon, end_lon]
            lats = [start_lat, end_lat]
 
        fig.add_trace(go.Scattergeo(locationmode='country names', lon=lons, lat=lats, mode='lines',
            line=dict(width=line_width, color=line_color,), hoverinfo='skip',showlegend=False))
 
    # Port names
    fig.add_trace(go.Scattergeo(
        locationmode='country names',
        lon=ports['Longitude'],
        lat=ports['Latitude'],
        mode='markers',
        marker=dict(
            size=5,  # Small size
            color='black',
            symbol='circle',
        ),
        name='LNG terminal',
        showlegend=True,
    ))

    fig.add_trace(go.Scattergeo(
        lon=[None],
        lat=[None],
        mode='lines',
        line=dict(width=2, color='gray'),
        name='Not included'
    ))

 
    # Add LNG import points
    for country, (lat, lon) in lng_import_coords.items():
        share_import = imports[imports['From']== country]['Share'].values
        capacity_import = imports[imports['From']== country]['Capacity_tot'].values
 
        # Condition, otherwise it does not work
        if len(capacity_import) > 0:
            capacity_import = capacity_import[0]  
        else:
            capacity_import = 0
 
        if len(share_import) > 0:
            share_import = share_import[0]  
        else:
            share_import = 0
 
        color = flow_color(share_import)
        size = max(10, 0.00005*capacity_import)
 
        fig.add_trace(go.Scattergeo(
            lon=[lon],
            lat=[lat],
            mode='markers',
            marker=dict(
                size=size,  
                color=color ,  
                symbol='circle',
                line=dict(width=0.5, color='black')
            ),
            hoverinfo='skip',
            showlegend=False
        ))
 
    # Size legend for small, medium, large
    fig.add_trace(go.Scattergeo(lon=[None], lat=[None], mode='markers',
        marker=dict(size=5, color='rgba(0,0,0,0)', symbol='circle', line=dict(width=0.5, color='black')),
        name='Low capacity', showlegend=True))

    fig.add_trace(go.Scattergeo(lon=[None], lat=[None], mode='markers',
        marker=dict(size=10, color='rgba(0,0,0,0)', symbol='circle', line=dict(width=0.5, color='black')),
        name='Medium capacity', showlegend=True))

    fig.add_trace(go.Scattergeo(lon=[None], lat=[None], mode='markers',
        marker=dict(size=20, color='rgba(0,0,0,0)', symbol='circle', line=dict(width=0.5, color='black')),
        name='High capacity', showlegend=True))


    fig.add_trace(go.Scattergeo(
    lon=[None],
    lat=[None],
    mode='lines',
    line=dict(width=0.1, color='rgba(0,0,0,0)'),  # invisible
    name='Width ∝ capacity',
    showlegend=True))
 
 
    # Add color bar to the legend
    colorscale = [[0.0, "rgb(0,160,0)"], # Green
    [0.5, "rgb(255,165,0)"],            # Orange
    [1.0, "rgb(220,50,50)"]]            # Soft red
 
    fig.add_trace(go.Scattergeo(
        lon=[None], lat=[None],  # no real data
        mode='markers',
        marker=dict(
            colorscale=colorscale,
            cmin=0,
            cmax=1,
            colorbar=dict(
                title=dict(
                text="Utilization",
                side="top"
                ),
                tickmode="array",
                orientation = 'h',
                tickvals=[0, 1],
                ticktext=["0%", "100%"],
                len=0.199,
                xpad = 0,
                thicknessmode = 'pixels',
                thickness = 10,
                x=0.964,  
                y=0.735,  
                xanchor='right',
                yanchor='top',
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='rgba(0, 0, 0, 0.8)',
                borderwidth=1,
            ),
            showscale=True,
            color=[0.5],  
            size=0.01,    
        ),
    showlegend=False,
    ))


    fig.update_layout(
        #title=title,
        geo=dict(
            scope='world',  # full world, but we control view
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(220, 230, 250)',
            showcountries=True,                 # Shows borders even internal
            countrycolor='rgb(180, 200, 230)',
            showcoastlines=True,
            coastlinecolor='rgb(160, 180, 220)',

            center=dict(lat=50, lon=20),  # Europe-focused
            lataxis=dict(range=[30, 65]),  # N Africa to N Europe
            lonaxis=dict(range=[-20, 40]), # W Europe to Central Asia
        ),
        width=900,
        height=650,
        legend=dict(
            x=0.965,  
            y=1.0,
            xanchor='right',
            yanchor='top',
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(0, 0, 0, 0.8)',
            borderwidth=1,
        )
    )
    fig.show()
    return fig

# Need to convert iso2 to iso3 country codes for plotly 
# Errors for EL and UK : need to change them for pycountry
def convert_to_alpha3(iso2):
    corrections = {
        "UK": "GB",  
        "EL": "GR", 
    }
    iso2 = corrections.get(iso2, iso2)
    try:
        return pycountry.countries.get(alpha_2=iso2).alpha_3
    except:
        return None


def plot_cost_map(input_path, scenario, output_path, geojson_path, save):
    output_file = os.path.join(output_path, "Costs_Results", f"cost_heatmap_{scenario}.png")

    with open(geojson_path, 'r', encoding='utf-8') as f:
        custom_geojson = json.load(f)

    df = pd.read_excel(input_path)
    df.columns = df.columns.str.strip()

    df = df[df["Node"].apply(european_countries)]
    df["Node_ISO3"] = df["Node"].apply(convert_to_alpha3)

    # Split Ukraine vs rest
    df_ukraine = df[df["Node_ISO3"] == "UKR"]
    df_rest = df[df["Node_ISO3"] != "UKR"]

    color_range = [11000, 35000]  
    # color_range = [df["Total Cost"].min(), df["Total Cost"].max()]

    fig = go.Figure()

    # Rest of Europe
    fig.add_trace(go.Choropleth(
        locations=df_rest["Node_ISO3"],
        z=df_rest["Total Cost"],
        colorscale="Viridis",
        zmin=color_range[0],
        zmax=color_range[1],
        marker_line_color='rgb(180, 200, 230)',
        marker_line_width=0.5,
        colorbar=dict(
            title="Total Cost (€)",
            titlefont=dict(size=14),
            tickfont=dict(size=12),
            len=0.6,
            y=0.5
        ),
        name="Rest of Europe"
    ))

    # Ukraine from GeoJSON
    fig.add_trace(go.Choropleth(
        geojson=custom_geojson,
        featureidkey="properties.GID_0",
        locations=df_ukraine["Node_ISO3"],
        z=df_ukraine["Total Cost"],
        colorscale="Viridis",
        zmin=color_range[0],
        zmax=color_range[1],
        marker_line_color='rgb(180, 200, 230)',
        marker_line_width=0,
        showscale=False,
        name="Ukraine"
    ))

    fig.update_layout(
        geo=dict(
            scope='europe',
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(220, 230, 250)',
            showcountries=True,
            countrycolor='rgb(180, 200, 230)',
            showcoastlines=True,
            coastlinecolor='rgb(160, 180, 220)',
            center=dict(lat=50, lon=20),
            lataxis=dict(range=[30, 65]),
            lonaxis=dict(range=[-20, 40]),
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        width=900,
        height=650
    )

    if save:
        fig.write_image(output_file, width=900, height=650, scale=2)
    else:
        fig.show()
     


def plot_cost_difference(input_difference, full_scenario_name, scenario, output_path, global_min, global_max, geojson_path, save):

    output_file = os.path.join(output_path, "Costs_Results", f"cost_difference_heatmap_{scenario}.png")
    
    with open(geojson_path, 'r', encoding='utf-8') as f:
        custom_geojson = json.load(f) 

    df = pd.read_excel(input_difference, sheet_name="Summary_Total_Cost")
    df.columns = df.columns.str.strip()

    df = df[df["Node"].apply(european_countries)]
    df["Node_ISO3"] = df["Node"].apply(convert_to_alpha3)

    df_ukraine = df[df["Node_ISO3"] == "UKR"]
    df_rest = df[df["Node_ISO3"] != "UKR"]
    
    color_range = [global_min, global_max]
    global_abs_max = max(abs(global_min), abs(global_max))

    percent_ticks = [-100, -50, 0, 50, 100]
    tickvals = [p / 100 * global_abs_max for p in percent_ticks]
    ticktext = [f"{p}%" for p in percent_ticks]

    middle_colorbar_normalized = (-color_range[0]) / (color_range[1] - color_range[0])
    colorscale = [
    [0.0, 'rgb(0, 128, 0)'],      
    [middle_colorbar_normalized, 'rgb(255, 255, 255)'],  
    [1.0, 'rgb(255, 0, 0)']]

    fig = go.Figure()

    # Trace for all other countries (Plotly built-in)
    fig.add_trace(go.Choropleth(
        locations=df_rest["Node_ISO3"],
        z=df_rest[full_scenario_name],
        colorscale=colorscale,
        zmin=color_range[0],
        zmax=color_range[1],
        marker_line_color='rgb(180, 200, 230)',
        marker_line_width=0.5,
        colorbar=dict(
            title="Cost difference (€)",
            titlefont=dict(size=14),
            tickfont=dict(size=12),
            len=0.6,
            y=0.5,
            x=0.0,
            tickvals=tickvals,   
            ticktext=ticktext 
        ),
    name="Rest of Europe"
    ))

    # Trace for Ukraine with custom GeoJSON
    fig.add_trace(go.Choropleth(
        geojson=custom_geojson,
        featureidkey="properties.GID_0",
        locations=df_ukraine["Node_ISO3"],
        z=df_ukraine[full_scenario_name],
        colorscale=colorscale,
        zmin=color_range[0],
        zmax=color_range[1],
        marker_line_color='rgb(180, 200, 230)',
        marker_line_width=0.25,
        showscale=False,  # Only one colorbar is needed (for the first trace)
        name="Ukraine"
    ))

    fig.update_layout(
        geo=dict(
            scope='world',  # or 'world'
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
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        width=900,
        height=650
    )

    if save:
        fig.write_image(output_file, width=900, height=650, scale=3)
        fig.show()
    else:
        fig.show()



# Plot utilization share by country as a bar chart for the investment scenario
def plot_bar_chart (df):
    # Add a color column based on Country
    df["Color"] = df["Country"].apply(
        lambda x: "green" if x == "Total" else
                  "orange" if x == "Total_EU" else
                  "royalblue"
    )

    # Create a bar chart for utilization share
    fig = px.bar(
        df,
        x="Country",
        y="Share",
        color = "Color",
        color_discrete_map="identity",
        labels={"Share": "Utilization Share", "Country": "Country"},
        text=df["Share"].apply(lambda x: f"{x:.0%}")
    )

    fig.update_traces(textposition='outside')
    fig.update_layout(
        yaxis_tickformat=".0%",
        yaxis_range=[0, 1.1],
        showlegend=False  # Hide the color legend
    )
    fig.show()
    return fig


def plot_emission_difference(emissions_df,base_year,base_scenario, path, save): 
    # Calculate the difference in Total_Emissions to the base year 2021
    emissions_df['Emissions_Diff_to_'+base_year] = emissions_df['Total_Emissions'] - emissions_df.loc[emissions_df['Scenario'] == base_scenario, 'Total_Emissions'].values[0]
    emissions_df['Color'] = 'royalblue'

    # Increase figure width and adjust margins to avoid overlap with legend and fit all numbers
    fig_emissions = px.bar(
        emissions_df,
        x='Scenario',
        y='Emissions_Diff_to_2021',
        title='Difference in Total Emissions Compared to ' + base_year,
        labels={'Emissions_Diff_to_2021': 'Emissions Difference to ' + base_year + 'in t', 'Year': 'Year'},
        text='Emissions_Diff_to_2021',
        color='Color',
        color_discrete_map="identity"
    )
    # Format the text to show values in millions, rounded
    fig_emissions.update_traces(
        texttemplate='%{text:.1f}M',
        textposition='outside',
        text=emissions_df['Emissions_Diff_to_'+base_year].apply(lambda x: round(x/1e6, 1))
    )
    fig_emissions.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        width=1100,  # Wider figure
        height=650,
        margin=dict(l=60, r=60, t=60, b=60),
        legend=dict(
            x=1.02,
            y=1,
            xanchor='left',
            yanchor='top'
        )
    )

    fig_emissions.update_layout(uniformtext_minsize=8, uniformtext_mode='hide') 

    fig_emissions.show()
    if save:
        output_file = os.path.join(path, "02_plots", "Flow_Results", f"emission_difference_{base_year}.png")
        fig_emissions.write_image(output_file, width=1135, height=800, scale=2)


def plot_emission_difference_factors(emissions_df, base_year, base_scenario, path, save):
    # Calculate emissions difference to base scenario
    emissions_df['Emissions_Diff_to_'+base_year] = (emissions_df['Total_Emissions'] - emissions_df.loc[emissions_df['Scenario'] == base_scenario, 'Total_Emissions'].values[0])
    emissions_df['Emissions_Diff_M'] = emissions_df['Emissions_Diff_to_'+base_year] / 1e6

    # Create subplot with secondary axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Emissions difference
    fig.add_trace(
        go.Bar(
            x=emissions_df['Scenario'],
            y=emissions_df['Emissions_Diff_M'],
            name='Emission difference',
            marker_color='royalblue',
            text=emissions_df['Emissions_Diff_M'].round(1),
            textposition='outside'
        ),
        secondary_y=False
    )

    # Emission factor EU
    fig.add_trace(
        go.Scatter(x=emissions_df['Scenario'], y=emissions_df['Emission_Factor_EU'], mode='lines+markers', name='Emission factor EU'), secondary_y=True)

    # Emission factor Europe
    fig.add_trace(
        go.Scatter(x=emissions_df['Scenario'], y=emissions_df['Emission_Factor_Europe'], mode='lines+markers', name='Emission factor Europe'), secondary_y=True)

    fig.update_layout(width=1100, height=650, margin=dict(l=60, r=60, t=60, b=60))
    fig.update_yaxes(title_text="Emissions Difference (Mt)", secondary_y=False)
    fig.update_yaxes(title_text="Average Emission Factor (tCO₂e/GWh)", range=[0, 58], secondary_y=True)

    fig.show()

    if save:
        output_file = os.path.join(path, "Flow_Results", f"emission_difference_{base_year}.png")
        fig.write_image(output_file, width=1135, height=800, scale=2)