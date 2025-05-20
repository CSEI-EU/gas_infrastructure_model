# import packages
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from plotly.colors import sample_colorscale, diverging
import plotly.express as px

import pycountry
from geopy.geocoders import Nominatim
import time


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
    'NO': (60.4720, 8.4689),
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
    'NO': (61.0, 10.0),
    'EE': (58.6, 26.0),  
    'TR': (38.0, 32.0)
}


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
def plot_flow_map(df, ports, imports, title):
    fig = go.Figure()
 
    # First plot the pipeline flows
    df_pipelines = df[(df['FromType'] == '-') & (df['ToType'] == '-')]
 
    for _, row in df_pipelines.iterrows():
        line_color = flow_color(row['Share'])
        line_width = max(row['Flow'] / 100000, 1.1) if row['Flow'] > 0 else 1
 
        fig.add_trace(go.Scattergeo(
            locationmode='country names',
            lon=[row['Source_lon'], row['Target_lon']],
            lat=[row['Source_lat'], row['Target_lat']],
            mode='lines',
            line=dict(
                width=line_width,
                color=line_color,
            ),
            hoverinfo='skip',
            showlegend=False,  # Do not show in legend
        ))
 
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
        #hoverinfo='skip',
        name='LNG terminal',
        showlegend=True,
    ))
 
    # Add LNG import points
    for country, (lat, lon) in LNG_IMPORT_COORDS.items():
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
    fig.add_trace(go.Scattergeo(
        lon=[None],
        lat=[None],
        mode='markers',
        marker=dict(
            size=5,
            color='rgba(0,0,0,0)',
            symbol='circle',
            line=dict(width=0.5, color='black')
        ),
        name='Low capacity',
        showlegend=True
    ))
 
    fig.add_trace(go.Scattergeo(
        lon=[None],
        lat=[None],
        mode='markers',
        marker=dict(
            size=10,
            color='rgba(0,0,0,0)',
            symbol='circle',
            line=dict(width=0.5, color='black')
        ),
        name='Medium capacity',
        showlegend=True
    ))
 
    fig.add_trace(go.Scattergeo(
        lon=[None],
        lat=[None],
        mode='markers',
        marker=dict(
            size=20,
            color='rgba(0,0,0,0)',
            symbol='circle',
            line=dict(width=0.5, color='black')
        ),
        name='High capacity',
        showlegend=True
    ))
 
 
    # Add color bar to the legend
    colorscale = [
    [0.0, "rgb(0,160,0)"],       # Green
    [0.5, "rgb(255,165,0)"],     # Orange
    [1.0, "rgb(220,50,50)"],     # Soft red
    ]
 
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
                ticktext=["Low", "High"],
                len=0.199,
                xpad = 0,
                thicknessmode = 'pixels',
                thickness = 10,
                x=0.964,  
                y=0.813,  
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

            # Gray disposition 
            #landcolor='rgb(200, 200, 200)',  
            #showcountries=True,            
            #countrycolor='rgb(169, 169, 169)',  
            #showcoastlines=True,
            #coastlinecolor='rgb(128, 128, 128)',

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


def plot_cost_map(input_path, scenario, base_path, save):
    output_file = os.path.join(base_path, "02_plots", "Costs_Results", f"cost_heatmap_{scenario}.png")
    df = pd.read_excel(input_path)
    df.columns = df.columns.str.strip()

    df = df[df["Node"].apply(european_countries)]
    df["Node_ISO3"] = df["Node"].apply(convert_to_alpha3)

    color_range = [11000, 35000] # color range from 2021
    # color_range = [df["Total Cost"].min(), df["Total Cost"].max()]

    fig = go.Figure(data=go.Choropleth(
        locations=df["Node_ISO3"],
        z=df["Total Cost"],
        colorscale="Viridis",
        zmin=color_range[0],
        zmax=color_range[1],
        marker_line_color='rgb(180, 200, 230)',  # country borders
        marker_line_width=0.5,
        colorbar=dict(
            title="Total Cost (€)",
            titlefont=dict(size=14),
            tickfont=dict(size=12),
            len=0.6,
            y=0.5
        ),
        geo='geo' 
    ))

    fig.update_layout(
        # title not shown
        geo=dict(
            scope='world',
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
        fig.write_image(output_file, width=1135, height=800, scale=2)
    else:
        fig.show()




def plot_cost_difference(input_difference, full_scenario_name, scenario, base_path, save):
    output_file = os.path.join(base_path, "02_plots", "Costs_Results", f"cost_difference_heatmap_{scenario}.png")
    
    df = pd.read_excel(input_difference, sheet_name="Summary_Total_Cost")
    df.columns = df.columns.str.strip()

    df = df[df["Node"].apply(european_countries)]
    df["Node_ISO3"] = df["Node"].apply(convert_to_alpha3)

    z = df[full_scenario_name]
    # color_range = [z.min(), z.max()]
    color_range = [-13000, 7000]

    # Green to red 
    colorscale = [
    [0.0, 'rgb(0, 128, 0)'],      # Green 
    [0.65, 'rgb(255, 255, 255)'],  # White 
    [1.0, 'rgb(255, 0, 0)'],      # Red 
    ]

    fig = go.Figure(data=go.Choropleth(
        locations=df["Node_ISO3"],
        z=z,
        colorscale=colorscale,
        zmin=color_range[0],
        zmax=color_range[1],
        marker_line_color='rgb(180, 200, 230)',  # country borders
        marker_line_width=0.5,
        colorbar=dict(
            title="Cost difference (€)",
            titlefont=dict(size=14),
            tickfont=dict(size=12),
            len=0.6,
            y=0.5
        ),
        geo='geo' 
    ))

    fig.update_layout(
        # title not shown
        geo=dict(
            scope='world',
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
        fig.write_image(output_file, width=1135, height=800, scale=2)
    else:
        fig.show()




# Plot utilization share by country as a bar chart for the investment scenario
def plot_bar_chart (df):
    # Create a bar chart for utilization share
    fig = px.bar(
        df,
        x="Country",
        y="Share",
        labels={"Share": "Utilization Share", "Country": "Country"},
        text=df["Share"].apply(lambda x: f"{x:.0%}")
    )
    fig.update_traces(textposition='outside', marker_color='royalblue')
    fig.update_layout(yaxis_tickformat=".0%", yaxis_range=[0, 1.1])
    fig.show()
    return fig






# Plot utilization share by country as a bar chart for the investment scenario

def plot_bar_chart (df):
    # Create a bar chart for utilization share
    fig = px.bar(
        df,
        x="Country",
        y="Share",
        labels={"Share": "Utilization Share", "Country": "Country"},
        text=df["Share"].apply(lambda x: f"{x:.0%}")
    )
    fig.update_traces(textposition='outside', marker_color='royalblue')
    fig.update_layout(yaxis_tickformat=".0%", yaxis_range=[0, 1.1])
    fig.show()
    return fig


# Old code with normal red to blue colors 
'''def flow_color(share):
    if share <= 0.0:
        return 'rgba(0, 255, 0, 0.8)'  # Green
    elif share >= 1.0:
        return 'rgba(255, 0, 0, 0.8)'  # Red

    if share < 0.5:
        # Green to Yellow
        ratio = share / 0.5
        r = int(255 * ratio)
        g = 255
        b = 0
    else:
        # Yellow to Red
        ratio = (share - 0.5) / 0.5
        r = 255
        g = int(255 * (1 - ratio))
        b = 0

    return f'rgba({r}, {g}, {b}, 0.7)'

    
# Final plot of the map
def plot_flow_map(df, ports, imports, title):
    fig = go.Figure()
 
    # First plot the pipeline flows
    df_pipelines = df[(df['FromType'] == '-') & (df['ToType'] == '-')]
 
    for _, row in df_pipelines.iterrows():
        line_color = flow_color(row['Share'])
        line_width = max(row['Flow'] / 100000, 1.1) if row['Flow'] > 0 else 1
 
        fig.add_trace(go.Scattergeo(
            locationmode='country names',
            lon=[row['Source_lon'], row['Target_lon']],
            lat=[row['Source_lat'], row['Target_lat']],
            mode='lines',
            line=dict(
                width=line_width,
                color=line_color,
            ),
            hoverinfo='skip',
            showlegend=False,  # Do not show in legend
        ))
 
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
        #hoverinfo='skip',
        name='LNG terminal',
        showlegend=True,
    ))
 
    # Add LNG import points
    for country, (lat, lon) in LNG_IMPORT_COORDS.items():
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
 
    # Size reference for small, medium, large
    small_size = 5
    medium_size = 10
    large_size = 20
 
    fig.add_trace(go.Scattergeo(
        lon=[None],
        lat=[None],
        mode='markers',
        marker=dict(
            size=small_size,
            color='rgba(0,0,0,0)',
            symbol='circle',
            line=dict(width=0.5, color='black')
        ),
        name='Low capacity',
        showlegend=True
    ))
 
    fig.add_trace(go.Scattergeo(
        lon=[None],
        lat=[None],
        mode='markers',
        marker=dict(
            size=medium_size,
            color='rgba(0,0,0,0)',
            symbol='circle',
            line=dict(width=0.5, color='black')
        ),
        name='Medium capacity',
        showlegend=True
    ))
 
    fig.add_trace(go.Scattergeo(
        lon=[None],
        lat=[None],
        mode='markers',
        marker=dict(
            size=large_size,
            color='rgba(0,0,0,0)',
            symbol='circle',
            line=dict(width=0.5, color='black')
        ),
        name='High capacity',
        showlegend=True
    ))
 
 
    # Add color bar to the legend
    colorscale = [
        [0.0, "rgb(0,255,0)"],      # Green
        [0.5, "rgb(255,255,0)"],    # Yellow
        [1.0, "rgb(255,0,0)"]       # Red
    ]
 
    fig.add_trace(go.Scattergeo(
        lon=[None], lat=[None],  # no real data
        mode='markers',
        marker=dict(
            colorscale=colorscale,
            cmin=0,
            cmax=1,
            colorbar=dict(
                title="Utilization",
                titleside="top",
                tickmode="array",
                orientation = 'h',
                tickvals=[0, 1],
                ticktext=["Low", "High"],
                len=0.199,
                xpad = 0,
                thicknessmode = 'pixels',
                thickness = 10,
                x=0.964,  
                y=0.813,  
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
        title=title,
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
'''