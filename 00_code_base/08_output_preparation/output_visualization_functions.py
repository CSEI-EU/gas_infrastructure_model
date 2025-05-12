# import packages
import pandas as pd
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pycountry
from geopy.geocoders import Nominatim
import time

# Pie chart of LNG sources for Leurope
def plot_pie_charts(df1, column1, year1, df2, column2, year2, country_map):
    grouped1 = df1.groupby('Region')[column1]
    grouped1.index = grouped1.index.map(lambda x: country_map.get(x, x))
    grouped2 = df2.groupby('Region')[column2]
    grouped2.index = grouped2.index.map(lambda x: country_map.get(x, x))   

    fig, axs = plt.subplots(1, 2, figsize=(14, 7))

    axs[0].pie(grouped1, labels=grouped1.index, autopct='%1.1f%%', startangle=90)
    axs[0].set_title(f"European LNG import sources ({year1})")

    axs[1].pie(grouped2, labels=grouped2.index, autopct='%1.1f%%', startangle=90)
    axs[1].set_title(f"European LNG import sources ({year2})")

    plt.tight_layout()
    plt.show()


# Try and plot with plotly to see difference
def plotly_pie_charts(df1, df2, flow_column, year1, year2):
    # Set dataframe indexes
    grouped1 = df1.set_index('Region')[flow_column]
    grouped2 = df2.set_index('Region')[flow_column]

    # Create pie charts
    fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]],subplot_titles=[str(year1), str(year2)])
    fig.add_trace(go.Pie(labels=grouped1.index, values=grouped1.values, name=str(year1)),row=1, col=1)
    fig.add_trace(go.Pie(labels=grouped2.index, values=grouped2.values, name=str(year2)),row=1, col=2)

    fig.update_layout(
        title_text=f"European LNG import sources: {year1} vs {year2}",
        annotations=[
            dict(text=str(year1), x=0.18, y=0.5, font_size=14, showarrow=False),
            dict(text=str(year2), x=0.82, y=0.5, font_size=14, showarrow=False)
        ]
    )
    fig.show()


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
def interesting_countries(code):
    return code in [
        'AL', 'AD', 'AM', 'AT', 'AZ', 'BY', 'BE', 'BA', 'BG', 'CH', 'CY', 'CZ',
        'DE', 'DK', 'DZ', 'EE', 'ES', 'FI', 'FR', 'GB', 'GE', 'GR', 'HR', 'HU', 'IE',
        'IS', 'IT', 'KZ', 'LI', 'LT', 'LU', 'LV', 'MA','MC', 'MD', 'ME', 'MK', 'MT',
        'NL', 'NO', 'PL', 'PT', 'RO', 'RS', 'RU', 'SE', 'SI', 'SK', 'SM', 'SU', 'TR',
        'UA', 'VA', 'XK'
    ]

def european_countries(code):
    return code in [
        'AL', 'AD', 'AM', 'AT', 'AZ', 'BY', 'BE', 'BA', 'BG', 'CH', 'CY', 'CZ',
        'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GB', 'GE', 'GR', 'HR', 'HU', 'IE',
        'IS', 'IT', 'LI', 'LT', 'LU', 'LV', 'MC', 'MD', 'ME', 'MK', 'MT',
        'NL', 'NO', 'PL', 'PT', 'RO', 'RS', 'RU', 'SE', 'SI', 'SK', 'SM', 'TR',
        'UA', 'VA', 'XK'
    ]

# Calculate the final capacity with and without investment 
def add_capacity_column(df, file_path):
    df = df.copy()
    file_name = os.path.basename(file_path)

    # When there is no investment, we only look at normal capacity
    if "inv" in file_name:
        df['Capacity'] = df['Changed Capacity'].fillna(0) + df['New Capacity'].fillna(0)
    else:
        df['Capacity'] = df['Changed Capacity']
    return df


# Then calulate the share column and add a column to the dataframe 
def add_share_column(df):
    df = df.copy()

    # Function to calculate the share
    def calculate_share(row):
        flow = row['Flow']
        capacity = row['Capacity']
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
    'CY': (35.1264, 33.4299),
    'CZ': (49.8175, 15.4730),
    'DE': (51.1657, 10.4515),
    'DK': (56.2639, 9.5018),
    'DZ': (28.0339, 1.6596),
    'EE': (58.5953, 25.0136),
    'ES': (40.4637, -3.7492),
    'FI': (61.9241, 25.7482),
    'FR': (46.6034, 1.8883),
    'GB': (55.3781, -3.4360),
    'GE': (42.3154, 43.3569),
    'GR': (39.0742, 21.8243),
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
    'SE': (60.1282, 18.6435),
    'SI': (46.1512, 14.9955),
    'SK': (48.6690, 19.6990),
    'SM': (43.9333, 12.4500),
    'SU': (55.0, 38.0),  
    'TR': (39.0, 35.0),
    'UA': (48.3794, 31.1656),
    'VA': (41.9029, 12.4534),
    'XK': (42.6026, 20.9020),
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
    'BE': (50.75, 4.0),
    'HR': (43.8, 16.0),
    'FI': (63.0, 26.0),
    'FR': (45.5, 2.0),
    'DE': (51.0, 10.0),
    'GR': (39.0, 21.5),
    'IT': (42.5, 13.5),
    'LT': (55.8, 23.7),
    'NL': (52.4, 5.0),
    'PL': (51, 21),
    'PT': (40.0, -8.0),
    'ES': (40, -2.0),
    'GB': (52.0, -2.5),
    'NO': (61.0, 10.0),
}

def get_lng_import_aggregates(df):
    df = df.copy()

    # Filter rows where either side is LNG import
    lng_imp_rows = df[(df['FromType'] == 'LNG_import') | (df['ToType'] == 'LNG_import')]

    # Extract country code 
    def get_lng_import_country(row):
        if row['FromType'] == 'LNG_import':
            return row['From']
        elif row['ToType'] == 'LNG_import':
            return row['To']
        return None

    lng_imp_rows['Country'] = lng_imp_rows.apply(get_lng_import_country, axis=1)
    lng_imp_rows = lng_imp_rows.dropna(subset=['Country'])


    # Aggregate by country: total capacity and weighted average share
    agg = lng_imp_rows.groupby('Country').agg(
        TotalCapacity=('Capacity', 'sum'),
        WeightedFlow=('Flow', 'sum')
    ).reset_index()
    agg['Share'] = agg['WeightedFlow'] / agg['TotalCapacity']
    
    return agg



# Color code for pipelines and LNG shares 
def flow_color(share):
    if share <= 0.0:
        return 'rgba(180, 180, 180, 0.4)'  # 0-flow: gray
    elif share < 0.5:
        return 'rgba(0, 128, 0, 0.8)'      # Green: low usage
    elif share < 0.75:
        return 'rgba(255, 165, 0, 0.8)'    # Orange: medium usage
    elif share <= 1.0:
        return 'rgba(255, 0, 0, 0.8)'      # Red: high usage


# Final plot of the map 
def plot_flow_map(df, ports, title):
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
            showlegend=False,  # Do not show these in the legend
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
        name='Ports',  # Name for legend
        hoverinfo='text',  # Display port name on hover
        text=ports['Name of \ninstallation'],  # Port names on hover
        showlegend=True,
    ))

    # Add LNG import points
    for country, (lat, lon) in LNG_IMPORT_COORDS.items():
        fig.add_trace(go.Scattergeo(
            lon=[lon],
            lat=[lat],
            mode='markers',
            marker=dict(
                size=5,  # Default small size
                color='blue',  # Temporary color
                symbol='circle',
                line=dict(width=0.5, color='black')
            ),
            name=f'{country} LNG Import',
            hoverinfo='text',
            text=f'{country}',  # Country code on hover
            showlegend=False
        ))

    # Add traces for legend only
    legend_items = [
        ('No-flow', 'rgba(180, 180, 180, 0.4)'),
        ('Low usage', 'rgba(0, 128, 0, 0.8)'),
        ('Medium usage', 'rgba(255, 165, 0, 0.8)'),
        ('High usage', 'rgba(255, 0, 0, 0.8)'),
    ]

    for label, color in legend_items:
        fig.add_trace(go.Scattergeo(
            lon=[None],  # No data to plot
            lat=[None],
            mode='lines',
            line=dict(
                width=1,
                color=color,
            ),
            name=label,
            showlegend=True,
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
            x=0.96,  
            y=1.0,  
            xanchor='right',
            yanchor='top',
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(0, 0, 0, 0.8)',
            borderwidth=1,
        )
    )

    fig.show()