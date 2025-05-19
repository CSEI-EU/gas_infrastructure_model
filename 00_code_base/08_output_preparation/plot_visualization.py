# import packages

import pandas as pd
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

os.chdir(r"C:\Users\flv.eco\OneDrive - CBS - Copenhagen Business School\Documents\03_LNG_Cap\hydrogen_grid\00_code_base\08_output_preparation")
from output_visualization_functions import *
from LNG_external_imports_functions import *
from year_difference_functions import *

base_path =r"C:\Users\flv.eco\OneDrive - CBS - Copenhagen Business School\Documents\03_LNG_Cap\hydrogen_grid"
#r"C:\Users\mar.eco\OneDrive - CBS - Copenhagen Business School\Desktop\hydrogen_grid"
#

# Import this for save funcroin to work
# pip install kaleido==0.1.0post1
save_flow_no_invest = True
file_name_no_invest = "outputs_IAEE_2025_run_2035_SP.png"
title_no_invest = "Cross-border NG flows in Stated Policies Scenario in 2035 "

save_flow_invest = False
file_name_invest = "Cross_border_flow_2024_invest.png"
title_invest = "Cross-border NG flows with investment in 2024"

output_path_no_invest = os.path.join(base_path, "02_plots", "Flow_Results", file_name_no_invest)
output_path_invest = os.path.join(base_path, "02_plots", "Flow_Results", file_name_invest)


input_LNG_file = os.path.join(base_path, "01_data", "01_input_data", "01_raw", "01_Russian_War_Case", "LNG_locations.xlsx")
output_file_no_invest = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "01_raw_results", "outputs_IAEE_2025_run_2035_SP.xlsx")
output_file_invest = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "01_raw_results", "outputs_IAEE_2025_run_2024_inv.xlsx")
output_2021 = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "02_prepared_results", "output_2021_prepared.xlsx")
output_2024 = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "02_prepared_results", "output_2024_prepared.xlsx")

df_output_2021 = pd.read_excel(output_2021,sheet_name='LNG_Sources')
df_output_2024 = pd.read_excel(output_2024, sheet_name='LNG_Sources')
flow_column = 'Flow (GWh).1'

country_map = {
    'AF': 'Africa', #@mathilde: I changed it as we cover Africa as a whole (except some countries like Egypt). 
    'EG': 'Egypt',
    'QA': 'Qatar',
    'TT': 'Trinidad & Tobago',
    'USA': 'United States'
    # Perhaps it is reasonable to add also the other export regions, even if they do not export to Europe (but might be possible)
}

#plot_pie_charts(df_output_2021, flow_column, 2021, df_output_2024, 'Flow (GWh).1', 2024, country_map)
#plotly_pie_charts(df_output_2021, df_output_2024, flow_column, 2021, 2024)


# -----------------------------------------------------------------------
# LNG terminals to show on the map 
years = [2024, 2021, 2035]
filtered_ports = filter_lng_ports_by_year(input_LNG_file, years)

# Change in Kollsnes 2 lon and Mukran lat 
filtered_ports.loc[filtered_ports['Name of \ninstallation'] == 'Kollsnes 1', 'Longitude'] += 0.4
filtered_ports.loc[filtered_ports['Name of \ninstallation'] == 'Kollsnes 2', 'Longitude'] += 0.4

filtered_ports['Name of \ninstallation'] = filtered_ports['Name of \ninstallation'].str.strip()
filtered_ports.loc[filtered_ports['Name of \ninstallation'] == 'Mukran FSRU Energos Power', 'Latitude'] -= 0.5
# Remove the second one (exactly the same)
filtered_ports = filtered_ports[filtered_ports['Name of \ninstallation'] != 'Mukran FSRU Neptune – 2nd']

# Change latitude in Mag Mell (Cork-IE)
filtered_ports.loc[filtered_ports['Name of \ninstallation'] == 'Mag Mell FSRU', 'Latitude'] += 0.5


title_ports = "LNG terminals addition over time"
plot_ports_by_year(filtered_ports, 2021, 2024, 2035, title=title_ports)


# -----------------------------------------------------------------------
df = pd.read_excel(output_file_no_invest)
df_methane = df[df['Commodity']=='Methane']
df_raw = parse_edges(df_methane)

# Check country codes and rows 
from_codes = df_raw['From'].unique()
to_codes = df_raw['To'].unique()
all_codes = set(from_codes) | set(to_codes)
#print(all_codes)

#----------------------------------------------------------------------
df_raw['FromType'] = df_raw['From'].apply(label_node_type)
df_raw['ToType'] = df_raw['To'].apply(label_node_type)
df_raw['From'] = df_raw['From'].apply(extract_country_code)
df_raw['To'] = df_raw['To'].apply(extract_country_code)

df_filtered = df_raw[df_raw['From'].apply(interesting_countries) & df_raw['To'].apply(european_countries)]
df_capacity = add_capacity_column(df_filtered, output_file_no_invest)
df_with_share = add_share_column(df_capacity)

# Add coordinates
df_with_coords = add_coordinates(df_with_share)

lng_import_rows = df_with_share[(df_with_share['FromType'] == 'LNG_import') | (df_with_share['ToType'] == 'LNG_import')]
df_with_imports = df_with_share[(df_with_share['FromType'] == 'LNG_import')]

# Plot
fig = plot_flow_map(df_with_coords, filtered_ports, df_with_imports, title_no_invest)

#Save the figure
if save_flow_no_invest: 
    df_with_imports.to_excel(output_path_no_invest.replace('.png', '_utilization_share.xlsx'), index=False)
    fig.write_image(output_path_no_invest, width=1135, height=800, scale=2)

# ---------------------------------------------------------------------
# Do all the same for the investment case 
df_invest = pd.read_excel(output_file_invest)
df_invest = df_invest[df_invest['Commodity']=='Methane']

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
fig = plot_flow_map(df_invest_with_coords, filtered_ports, df_with_imports, title = title_invest)

if save_flow_invest: 
    df_invest_with_share.to_excel(output_path_invest.replace('.png', '_utilization_share.xlsx'), index=False)
    fig.write_image(output_path_invest, width=1135, height=800, scale=2)
