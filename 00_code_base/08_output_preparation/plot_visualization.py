# import packages
import pandas as pd
import os

# os.chdir(r"C:\Users\flv.eco\OneDrive - CBS - Copenhagen Business School\Documents\03_LNG_Cap\hydrogen_grid\00_code_base\08_output_preparation")
from output_visualization_functions import *
from LNG_external_imports_functions import *
from year_difference_functions import *

# base_path =r"C:\Users\flv.eco\OneDrive - CBS - Copenhagen Business School\Documents\03_LNG_Cap\hydrogen_grid"
base_path = r"C:\Users\mar.eco\OneDrive - CBS - Copenhagen Business School\Desktop\hydrogen_grid"
#

# Import this for save funcroin to work
# pip install kaleido==0.1.0post1

years = [2021, 2024, 2035]
save_flow_no_invest = False 
file_name_no_invest = "outputs_IAEE_2025_run_2035_AP"

save_flow_invest = False
file_name_invest = "outputs_IAEE_2025_run_2035_SP"

output_path_no_invest = os.path.join(base_path, "02_plots", "Flow_Results", file_name_no_invest)
output_path_invest = os.path.join(base_path, "02_plots", "Flow_Results", file_name_invest)
output_path_xlsx = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "02_prepared_results", file_name_no_invest+"_utilization_share.xlsx")
output_path_invest_xlsx = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "02_prepared_results", file_name_invest+"_utilization_share.xlsx")

input_excluded_pipelines = os.path.join(base_path, "01_data", "01_input_data", "01_raw", "01_Russian_War_Case", "information_pipelines_exclude_from_plots.xlsx")
baseline_file_2021 = "outputs_IAEE_2025_run_2021"
baseline_path_2021 = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "01_raw_results", baseline_file_2021+ ".xlsx")
baseline_file_2024 = "outputs_IAEE_2025_run_2024"
baseline_path_2024 = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "01_raw_results", baseline_file_2024+ ".xlsx")
baseline_file_2035 = "outputs_IAEE_2025_run_2035_SP"
baseline_path_2035 = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "01_raw_results", baseline_file_2035+ ".xlsx")


input_LNG_file = os.path.join(base_path, "01_data", "01_input_data", "01_raw", "01_Russian_War_Case", "LNG_locations.xlsx")
output_file_no_invest = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "01_raw_results", file_name_no_invest+ ".xlsx")
output_file_invest = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "01_raw_results", file_name_invest+".xlsx")
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

countries_with_terminals = get_countries_with_terminals(filtered_ports)
countries_iso2 = set(filter(None, [country_name_to_code(name) for name in countries_with_terminals]))
filtered_LNG_IMPORT_COORDS = { country: coords for country, coords in LNG_IMPORT_COORDS.items() if country in countries_iso2}

# -----------------------------------------------------------------
# Plot three maps showng differences 
df_ports_2021 = identify_terminal_status(filtered_ports[filtered_ports['Model Year'] <= 2021], 2021)
df_2021 = process_file(baseline_path_2021)
pipelines_2021 = df_2021[(df_2021['FromType'] == '-') & (df_2021['ToType'] == '-')]
pipeline_status_2021 = {edge: 'included' for edge in pipelines_2021['Edge']}

df_ports_2024 = identify_terminal_status(filtered_ports[filtered_ports['Model Year'] <= 2024], 2024)
df_2024 = process_file(baseline_path_2024)
pipelines_2024 = df_2024[(df_2024['FromType'] == '-') & (df_2024['ToType'] == '-')]
pipeline_status_2024 = scenario_pipeline_exclusions(input_excluded_pipelines, pipelines_2024['Edge'].dropna().unique())

df_ports_2035 = identify_terminal_status(filtered_ports, 2035)
df_2035 = process_file(baseline_path_2035)
pipelines_2035 = df_2035[(df_2035['FromType'] == '-') & (df_2035['ToType'] == '-')]
pipeline_status_2035 = {edge: 'included' for edge in pipelines_2035['Edge']}

#plot_map(df_ports_2021, pipelines_2021, pipeline_status_2021, 2021, base_path, False)
#plot_map(df_ports_2024, pipelines_2024, pipeline_status_2024, 2024, base_path, False)
#plot_map(df_ports_2035, pipelines_2035, pipeline_status_2035, 2035, base_path, False)



# -----------------------------------------------------------------------
df_no_invest = process_file(output_file_no_invest)
df_with_imports = df_no_invest[(df_no_invest['FromType'] == 'LNG_import')]

# Filter out rows to save
utilization_df = df_with_imports[["From", "Flow", "Capacity_tot", "Share"]]
utilization_df.rename(columns={"From": "Country"}, inplace=True)
utilization_df.sort_values(by="Country", ascending=True, inplace=True)

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

# Consider the pipelines excluded in each scenario
df_final = process_pipelines(df_no_invest, file_name_no_invest, input_excluded_pipelines)

# Plot
fig = plot_flow_map(df_final, filtered_ports, df_with_imports, filtered_LNG_IMPORT_COORDS)

#Save the figure
if save_flow_no_invest: 
    fig.write_image(output_path_no_invest + ".png", width=900, height=650, scale=2)
    utilization_summary.to_excel(output_path_xlsx, index=False)
    bar_fig.write_image(output_path_no_invest + '_bar_chart.png', width=1135, height=800, scale=2)

# ---------------------------------------------------------------------
# Do all the same for the investment case 
df_invest = process_file(output_file_invest)
df_with_imports_invest = df_invest[(df_invest['FromType'] == 'LNG_import')]

# Filter out rows to save
utilization_invest_df = df_with_imports_invest[["From", "Flow", "Capacity_tot", "Share"]]
utilization_invest_df.rename(columns={"From": "Country"}, inplace=True)
utilization_invest_df.sort_values(by="Country", ascending=True, inplace=True)

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

# Consider the pipelines excluded in each scenario
df_clean = process_pipelines(df_invest, file_name_invest, input_excluded_pipelines)

# Plot
fig = plot_flow_map(df_clean, filtered_ports, df_with_imports, filtered_LNG_IMPORT_COORDS)

if save_flow_invest: 
    fig.write_image(output_path_invest + ".png", width=900, height=650, scale=2)
    utilization_summary_invest.to_excel(output_path_invest_xlsx, index=False)
    bar_fig.write_image(output_path_invest + '_bar_chart.png', width=1135, height=800, scale=2)


# ---------------------------------------------------------------------
import requests

url = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_UKR_0.json"
json_file_path = os.path.join(base_path, "00_code_base", "08_output_preparation", "gadm41_UKR_0.json")
response = requests.get(url)
with open(json_file_path, "wb") as f:
    f.write(response.content)

print("JSON File downloaded successfully")

data_path = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "02_prepared_results")
scenario = "2024_plus_NO_reduced"
full_name = "costs_shares_IAEE_2025_run_2024_plus_NO_reduced"
input_file_cost = os.path.join(data_path, "costs_shares_IAEE_2025_run_2024_plus_NO_reduced.xlsx")

file_cost_difference_2021 = os.path.join(data_path, "cost_shares_differences_to_2021.xlsx")
file_cost_difference_2024 = os.path.join(data_path, "cost_shares_differences_to_2024.xlsx")
file_cost_difference_2035 = os.path.join(data_path, "cost_shares_differences_to_2035_SP.xlsx")

colorbar_zero_2021 = 0.32
colorbar_zero_2024 = 0.65
colorbar_zero_2035 = 0.77

global_min_2021 = -13700
global_max_2021 = 11875
global_min_2024 = -13700
global_max_2024 = 10500

# plot_cost_map(input_file_cost, scenario, base_path, json_file_path, True)
plot_cost_difference(file_cost_difference_2024, full_name, scenario, base_path, global_min_2024, global_max_2024, json_file_path, True)

# ---------------------------------------------------------------------
data_path_emissions = os.path.join(base_path, "01_data", "02_output_data", "02_unidirectional_results", "01_paper_IAEE", "02_prepared_results")
input_file_emissions= os.path.join(data_path_emissions, "emission_differences.xlsx")

emissions_diff = pd.read_excel(input_file_emissions)
emissions_diff.loc[emissions_diff['Scenario'] == '2021', 'Scenario'] = '2021 - 1. Baseline'
emissions_diff.loc[emissions_diff['Scenario'] == '2024', 'Scenario'] = '2024 - 2. No Russian imports'
emissions_diff.loc[emissions_diff['Scenario'] == '2024_inv', 'Scenario'] = '2024 - 3. No Russian imports with investments'
emissions_diff.loc[emissions_diff['Scenario'] == '2024_no_QA', 'Scenario'] = '2024 - 2.2. No Qatari imports'
emissions_diff.loc[emissions_diff['Scenario'] == '2024_NO_red', 'Scenario'] = '2024 - 2.3. Reduced Norwegian pipeline exports'
emissions_diff.loc[emissions_diff['Scenario'] == '2024_no_USA', 'Scenario'] = '2024 - 2.1. NO US imports'
emissions_diff.loc[emissions_diff['Scenario'] == '2024_with_RU', 'Scenario'] = '2024 - 2.4. Limited Russian imports'
emissions_diff.loc[emissions_diff['Scenario'] == '2035_SP', 'Scenario'] = '2035 - 4.1. IEA - SP'
emissions_diff.loc[emissions_diff['Scenario'] == '2035_AP', 'Scenario'] = '2035 - 4.2. IEA - AP'  

emissions_diff.sort_values(by='Scenario', inplace=True)

# plot_emission_difference(emissions_diff, "2021",'2021 - 1. Baseline', base_path, False)
