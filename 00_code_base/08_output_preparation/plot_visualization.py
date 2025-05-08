# import packages
import pandas as pd
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from output_visualization_functions import *


base_path = r"C:\Users\mar.eco\OneDrive - CBS - Copenhagen Business School\Desktop\hydrogen_grid"

input_file = os.path.join(base_path, "01_data", "01_input_data", "02_processed", "01_paper_IAEE", "inputs_IAEE_2025_run_2024.xlsx")
output_file_no_invest = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "01_raw_results", "raw_no_investments_2024.csv")
output_file_invest = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "01_raw_results", "raw_investments_2021.csv")
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


df = pd.read_csv(output_file_no_invest)
df_raw = parse_edges(df)
df_raw['EdgeType'] = df_raw.apply(label_edge_type, axis=1)
print(df_raw)
#df_raw['From'] = df_raw['From'].apply(extract_country_code)
#df_raw['To'] = df_raw['To'].apply(extract_country_code)

df_filtered = df_raw[df_raw['From'].apply(interesting_countries) & df_raw['To'].apply(interesting_countries)]
df_capacity = add_capacity_column(df_filtered, output_file_no_invest)
#df_with_share = add_share_column(df_capacity)

# Add coordinates
geolocator = Nominatim(user_agent="pipeline_map_app")
#df_with_coords = add_coordinates(df_with_share)


# Plot
title = "LNG flows without Investment (2024)"
#plot_flow_map(df_with_coords, title=title)
