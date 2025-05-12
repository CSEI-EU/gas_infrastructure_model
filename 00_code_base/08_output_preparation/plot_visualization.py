# import packages
import pandas as pd
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from output_visualization_functions import *


base_path = r"C:\Users\mar.eco\OneDrive - CBS - Copenhagen Business School\Desktop\hydrogen_grid"

input_LNG_file = os.path.join(base_path, "01_data", "01_input_data", "01_raw", "01_Russian_War_Case", "LNG_locations.xlsx")
output_file_no_invest = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "01_raw_results", "outputs_IAEE_2025_run_2024.xlsx")
output_file_invest = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "01_raw_results", "outputs_IAEE_2025_run_2024_inv.xlsx")
output_2021 = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "02_prepared_results", "output_2021_prepared.xlsx")
output_2024 = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "02_prepared_results", "output_2024_prepared.xlsx")

df_output_2021 = pd.read_excel(output_2021,sheet_name='LNG_Sources')
df_output_2024 = pd.read_excel(output_2024, sheet_name='LNG_Sources')
flow_column = 'Flow (GWh).1'

country_map = {
    'AF': 'Afghanistan',
    'EG': 'Egypt',
    'QA': 'Qatar',
    'TT': 'Trinidad & Tobago',
    'USA': 'United States'
}

#plot_pie_charts(df_output_2021, flow_column, 2021, df_output_2024, 'Flow (GWh).1', 2024, country_map)
#plotly_pie_charts(df_output_2021, df_output_2024, flow_column, 2021, 2024)

years = [2024, 2021]
filtered_ports = filter_lng_ports_by_year(input_LNG_file, years)
#print(filtered_ports.head())


df = pd.read_excel(output_file_no_invest)
df_raw = parse_edges(df)
df_raw['FromType'] = df_raw['From'].apply(label_node_type)
df_raw['ToType'] = df_raw['To'].apply(label_node_type)
df_raw['From'] = df_raw['From'].apply(extract_country_code)
df_raw['To'] = df_raw['To'].apply(extract_country_code)

#df_filtered = df_raw
df_filtered = df_raw[df_raw['From'].apply(interesting_countries) & df_raw['To'].apply(european_countries)]
df_capacity = add_capacity_column(df_filtered, output_file_no_invest)
df_with_share = add_share_column(df_capacity)
#print(df_with_share.head(10))

# Add coordinates
df_with_coords = add_coordinates(df_with_share)


# Plot
title = "LNG flows without investment (2024)"
plot_flow_map(df_with_coords, filtered_ports, title)


# ---------------------------------------------------------------------
# Do all the same for the investment case 
df_invest = pd.read_excel(output_file_invest)

df_invest_raw = parse_edges(df_invest)
df_invest_raw['FromType'] = df_invest_raw['From'].apply(label_node_type)
df_invest_raw['ToType'] = df_invest_raw['To'].apply(label_node_type)
df_invest_raw['From'] = df_invest_raw['From'].apply(extract_country_code)
df_invest_raw['To'] = df_invest_raw['To'].apply(extract_country_code)

# Filter the rows based on the countries of interest (same as before)
df_invest_filtered = df_invest_raw[df_invest_raw['From'].apply(interesting_countries) & df_invest_raw['To'].apply(european_countries)]
df_invest_capacity = add_capacity_column(df_invest_filtered, output_file_invest)
df_invest_with_share = add_share_column(df_invest_capacity)

# Add coordinates 
df_invest_with_coords = add_coordinates(df_invest_with_share)

# Plot the flow map for the "investment" scenario
title_invest = "LNG flows with investment (2024)"
#plot_flow_map(df_invest_with_coords, title=title_invest)
#plot_flow_map(df_invest_with_coords, filtered_ports, title_invest)
