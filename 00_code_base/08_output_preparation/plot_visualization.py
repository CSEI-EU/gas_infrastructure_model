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
# base_path = r"C:\Users\mar.eco\OneDrive - CBS - Copenhagen Business School\Desktop\hydrogen_grid"
#

# Import this for save funcroin to work
# pip install kaleido==0.1.0post1
save_flow_no_invest = False 
file_name_no_invest = "outputs_IAEE_2025_run_2035_SP.png"
title_no_invest = "Cross-border NG flows in Stated Policies Scenario in 2035"

save_flow_invest = False
file_name_invest = "Cross_border_flow_2024_invest.png"
title_invest = "Cross-border NG flows with investment in 2024"

output_path_no_invest = os.path.join(base_path, "02_plots", "Flow_Results", file_name_no_invest)
output_path_invest = os.path.join(base_path, "02_plots", "Flow_Results", file_name_invest)
output_path_xlsx = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "02_prepared_results", file_name_no_invest+"_utilization_share.xlsx")
output_path_invest_xlsx = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "02_prepared_results", file_name_invest+"_utilization_share.xlsx")


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

# Filter out rows to save
utilization_df = df_with_imports[["From", "Flow", "Capacity_tot", "Share"]]
utilization_df.rename(columns={"From": "Country"}, inplace=True)

# Calculate total Flow and Capacity
total_flow = utilization_df["Flow"].sum()
total_capacity = utilization_df["Capacity_tot"].sum()

total_flow_EU = utilization_df[utilization_df.Country.apply(eu_countries)].Flow.sum()
total_capacity_EU = utilization_df[utilization_df.Country.apply(eu_countries)].Capacity_tot.sum()


# Calculate utilization share
total_share = total_flow / total_capacity if total_capacity != 0 else 0
total_share_EU = total_flow_EU / total_capacity_EU if total_capacity_EU != 0 else 0

# Create a summary row
summary_row = pd.DataFrame({
    "Country": ["Total"],
    "Flow": [total_flow],
    "Capacity_tot": [total_capacity],
    "Share": [total_share]
})
summary_row_EU = pd.DataFrame({
    "Country": ["Total_EU"],
    "Flow": [total_flow_EU],
    "Capacity_tot": [total_capacity_EU],
    "Share": [total_share_EU]
})

# Append the summary to the DataFrame
utilization_summary = pd.concat([utilization_df, summary_row, summary_row_EU], ignore_index=True)
bar_fig = plot_bar_chart(utilization_summary)

# Plot
fig = plot_flow_map(df_with_coords, filtered_ports, df_with_imports, title_no_invest)

#Save the figure
if save_flow_no_invest: 
    fig.write_image(output_path_no_invest, width=1135, height=800, scale=2)
    utilization_summary.to_excel(output_path_xlsx, index=False)
    bar_fig.write_image(output_path_no_invest.replace('.png', '_bar_chart.png'), width=1135, height=800, scale=2)

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
lng_import_rows_invest = df_invest_with_share[(df_invest_with_share['FromType'] == 'LNG_import') | (df_invest_with_share['ToType'] == 'LNG_import')]

# Why do we deen to filter in this way? With this procdure we drop information on non European LNG Terminals?
# @Mathilde
df_with_imports_invest = df_invest_with_share[(df_invest_with_share['FromType'] == 'LNG_import')]
df_with_imports_invest.drop(df_with_imports_invest[df_with_imports_invest['Flow'] == 0].index, inplace=True)

# Filter out rows to save
utilization_invest_df = df_with_imports_invest[["From", "Flow", "Capacity_tot", "Share"]]
utilization_invest_df.rename(columns={"From": "Country"}, inplace=True)

# Calculate total Flow and Capacity
total_flow_invest = utilization_invest_df["Flow"].sum()
total_capacity_invest = utilization_invest_df["Capacity_tot"].sum()

total_flow_EU_invest  = utilization_invest_df[utilization_invest_df.Country.apply(eu_countries)].Flow.sum()
total_capacity_EU_invest  = utilization_invest_df[utilization_invest_df.Country.apply(eu_countries)].Capacity_tot.sum()


# Calculate utilization share
total_share_invest = total_flow_invest / total_capacity_invest if total_capacity_invest != 0 else 0
total_share_EU_invest = total_flow_EU_invest / total_capacity_EU_invest if total_capacity_EU_invest != 0 else 0

# Create a summary row
summary_row_invest = pd.DataFrame({
    "Country": ["Total"],
    "Flow": [total_flow_invest],
    "Capacity_tot": [total_capacity_invest],
    "Share": [total_share_invest]
})
summary_row_EU_invest = pd.DataFrame({
    "Country": ["Total_EU"],
    "Flow": [total_flow_EU_invest],
    "Capacity_tot": [total_capacity_EU_invest],
    "Share": [total_share_EU_invest]
})

# Append the summary to the DataFrame
utilization_summary_invest = pd.concat([utilization_invest_df, summary_row_invest, summary_row_EU_invest], ignore_index=True)
bar_fig = plot_bar_chart(utilization_summary_invest)

# Plot the flow map for the "investment" scenario
fig = plot_flow_map(df_invest_with_coords, filtered_ports, df_with_imports_invest, title = title_invest)

if save_flow_invest: 
    fig.write_image(output_path_invest, width=1135, height=800, scale=2)
    utilization_summary_invest.to_excel(output_path_invest_xlsx, index=False)
    bar_fig.write_image(output_path_invest.replace('.png', '_bar_chart.png'), width=1135, height=800, scale=2)




data_path = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "02_prepared_results")
scenario = "2024_plus_no_USA"
full_name = "costs_shares_IAEE_2025_run_2024_plus_no_USA"
input_file_cost = os.path.join(data_path, "costs_shares_IAEE_2025_run_2024_plus_no_USA.xlsx")

file_cost_difference_2021 = os.path.join(data_path, "cost_shares_differences_to_2021.xlsx")
file_cost_difference_2024 = os.path.join(data_path, "cost_shares_differences_to_2024.xlsx")
ile_cost_difference_2035 = os.path.join(data_path, "cost_shares_differences_to_2035_SP.xlsx")

# plot_cost_map(input_file_cost, scenario, base_path, False)
plot_cost_difference(file_cost_difference_2024, full_name, scenario, base_path, True)