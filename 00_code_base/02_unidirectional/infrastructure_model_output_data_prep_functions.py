'''
This is the gas and hydrogen infrastructure of CSEI, an open-source Tool
for analyzing different aspects of the infrastructure. Examples are the 
development, including the conversion of the natural gas to a hydrogen grid, 
or the supply situation in Europe. The tool is developed at the Copenhagen 
School of Energy Infrastructure at the Copenhagen Business School.
---------------------------------------
Functions File for the data import:
The functions include the logical prossecing, mathematical calculation
logic for the preparation of the input data file for the model runs.
SPDX-FileCopyrightText: Johannes Giehl <jfg.eco@cbs.dk>
SPDX-License-Identifier: GNU GENERAL PUBLIC LICENSE GPL 3.0
'''

# import packages
import pandas as pd
from gurobipy import GRB

#define function

def check_optimization_status(model):
    # ANSI escape codes for color and bold
    GREEN_BOLD = '\033[1;32m'  # Green and Bold
    RED_BOLD = '\033[1;31m'    # Red and Bold
    RESET = '\033[0m'          # Reset to default color and style
    
    # Check if the model has an optimal solution
    if model.status == GRB.OPTIMAL:
        print(f"{GREEN_BOLD}Optimal solution found!{RESET}")
    else:
        print(f"{RED_BOLD}No optimal solution found.{RESET}")

def store_optimization_results(model, commodities, network_edges, excess_edges, shortage_edges, x_flow, y_new_cap, Change, z_conv_cap, x_flow_excess, x_flow_shortage):
    # Create lists to store the data
    results_data = []
    columns = ["Commodity", "Edge", "Flow", "New Capacity", "Switched", "Changed Capacity"]
    excess_data = []
    excess_columns = ["Commodity", "Edge", "Flow"]
    shortage_data = []
    shortage_columns = ["Commodity", "Edge", "Flow"]
    
    # Check if the model has an optimal solution
    if model.status == GRB.OPTIMAL:
        for commodity in commodities:
            for edge in network_edges:
                # Append data to the results list
                results_data.append([commodity,
                                     edge, 
                                     x_flow[commodity][edge].x, 
                                     y_new_cap[commodity][edge].x, 
                                     Change[commodity][edge].x, 
                                     z_conv_cap[commodity][edge].x])
        for edge in excess_edges:    
            excess_data.append([commodity, 
                                edge, 
                                x_flow_excess[commodity][edge].x])
        for edge in shortage_edges:    
            shortage_data.append([commodity, 
                                  edge, 
                                  x_flow_shortage[commodity][edge].x])
        
        # Create DataFrames from the collected data
        results_df = pd.DataFrame(results_data, columns=columns)
        excess_df = pd.DataFrame(excess_data, columns=excess_columns)
        shortage_df = pd.DataFrame(shortage_data, columns=shortage_columns)
        
        # Return DataFrames
        return results_df, excess_df, shortage_df
    else:
        print("No optimal solution found.")
        return None, None, None

def filter_commodities_to_dataframe(results_df, commodity_list):
    # Create an empty dictionary to store DataFrames for each commodity
    commodity_dfs = {}
    
    # Loop through the commodity list and filter the results_df
    for commodity in commodity_list:
        commodity_rows_df = results_df[results_df['Commodity'].str.contains(commodity, case=False)]
        
        # Drop unwanted columns for the commodity DataFrame
        commodity_rows_df = commodity_rows_df.drop(columns=['New Capacity', 'Switched', 'Changed Capacity'])
        
        # Store the DataFrame in the dictionary
        commodity_dfs[commodity] = commodity_rows_df
    
    return commodity_dfs

def add_share_column(df, initial_capacities_data):
    # Function to calculate the share of the use of each infrastructure element
    def calculate_share(row, initial_capacities_data):
        commodity = row['Commodity']
        edge_tuple = row['Edge']
        edge = ','.join(edge_tuple)  # Convert tuple to string in the format "Source,Destination"
        flow = row['Flow']
        
        # Check if the commodity and edge exist in the initial capacities data
        if commodity in initial_capacities_data and edge in initial_capacities_data[commodity]:
            capacity = initial_capacities_data[commodity][edge]
            # Return the share of the flow relative to the capacity, avoid division by zero
            return flow / capacity if capacity != 0 else 0
        return None  # Return None if no matching capacity is found

    # Apply the 'calculate_share' function to each row and create a new 'Share' column
    df['Share'] = df.apply(calculate_share, axis=1, initial_capacities_data=initial_capacities_data)
    return df

# Function to calculate aggregated share by type and commodity, excluding specific countries
def calculate_aggregated_share_supply(df, node_values, countries=[]):
    # Initialize a dictionary to store results
    result_data = {
        'Commodity': [],
        'Type': [],
        'Total Flow': [],
        'Total Potential Supply': [],
        'Share': []
    }
    
    # Group dataframe by commodity
    grouped_df = df.groupby('Commodity')
    
    # Iterate over each commodity group
    for commodity, group in grouped_df:
        # Initialize dictionaries to store total capacities and flows for each type
        total_capacities = {'LNG': 0, 'Prod': 0, 'St': 0}
        total_flows = {'LNG': 0, 'Prod': 0, 'St': 0}
        
        # Sum capacities from the node_values dictionary by type for this commodity, excluding specified countries
        if commodity in node_values:  # Ensure the commodity exists in the dictionary
            for node, capacity in node_values[commodity].items():
                parts = node.split('_')
                if len(parts) > 1:  # Ensure there is a type
                    country_code = parts[0]  # Extract country code (e.g., 'BE')
                    node_type = parts[1]     # Extract type (e.g., 'LNG', 'Prod')
                    if country_code in countries:  # Skip if the country is in the exclusion list
                        continue
                    if node_type in total_capacities:
                        total_capacities[node_type] += capacity
        
        # Sum flows from the dataframe by type for this commodity, excluding specified countries
        for _, row in group.iterrows():
            edge_tuple = row['Edge']
            node_name = edge_tuple[0]  # Take the first part of the tuple (e.g., 'BE_LNG')
            country_code = edge_tuple[1]  # Take the country code (e.g., 'BE')
            if country_code in countries:  # Skip if the country is in the exclusion list
                continue
            parts = node_name.split('_')
            if len(parts) > 1:  # Ensure there is a type
                node_type = parts[1]
                if node_type in total_flows:
                    total_flows[node_type] += row['Flow']
        
        # Calculate shares and store results for this commodity
        for node_type in total_capacities:
            total_flow = total_flows[node_type]
            total_potential_supply = total_capacities[node_type]
            share = total_flow / total_potential_supply if total_potential_supply != 0 else 0
            result_data['Commodity'].append(commodity)
            result_data['Type'].append(node_type)
            result_data['Total Flow'].append(total_flow)
            result_data['Total Potential Supply'].append(total_potential_supply)
            result_data['Share'].append(share)
    
    # Create a new dataframe from the result data
    result_df = pd.DataFrame(result_data)
    return result_df

# Function to calculate aggregated share by type and commodity, excluding specific countries
def calculate_aggregated_capacity(df, capacities_data, countries=[]):
    # Initialize a dictionary to store results
    result_data = {
        'Commodity': [],
        'Type': [],
        'Total Flow': [],
        'Total Capacity': [],
        'Share': []
    }
    
    # Group dataframe by commodity
    grouped_df = df.groupby('Commodity')
    
    # Iterate over each commodity group
    for commodity, group in grouped_df:
        # Initialize dictionaries to store total capacities and flows for each type
        total_capacities = {'LNG': 0, 'Prod': 0, 'St': 0}
        total_flows = {'LNG': 0, 'Prod': 0, 'St': 0}
        
        # Sum capacities from the nested dictionary by type for this commodity, excluding specified countries
        if commodity in capacities_data:  # Ensure the commodity exists in the dictionary
            for edge, capacity in capacities_data[commodity].items():
                edge_parts = edge.split(',')
                edge_prefix = edge_parts[0]  # Take the part before the comma (e.g., 'BE_LNG')
                country_code = edge_parts[1]  # Take the country code (e.g., 'BE')
                if country_code in countries:  # Skip if the country is in the exclusion list
                    continue
                parts = edge_prefix.split('_')
                if len(parts) > 1:  # Ensure there is a type
                    edge_type = parts[1]
                    if edge_type in total_capacities:
                        total_capacities[edge_type] += capacity
        
        # Sum flows from the dataframe by type for this commodity, excluding specified countries
        for _, row in group.iterrows():
            edge_tuple = row['Edge']
            edge_prefix = edge_tuple[0]  # Take the first part of the tuple (e.g., 'BE_LNG')
            country_code = edge_tuple[1]  # Take the country code (e.g., 'BE')
            if country_code in countries:  # Skip if the country is in the exclusion list
                continue
            parts = edge_prefix.split('_')
            if len(parts) > 1:  # Ensure there is a type
                edge_type = parts[1]
                if edge_type in total_flows:
                    total_flows[edge_type] += row['Flow']
        
        # Calculate shares and store results for this commodity
        for edge_type in total_capacities:
            total_flow = total_flows[edge_type]
            total_capacity = total_capacities[edge_type]
            share = total_flow / total_capacity if total_capacity != 0 else 0
            result_data['Commodity'].append(commodity)
            result_data['Type'].append(edge_type)
            result_data['Total Flow'].append(total_flow)
            result_data['Total Capacity'].append(total_capacity)
            result_data['Share'].append(share)
    
    # Create a new dataframe from the result data
    result_df = pd.DataFrame(result_data)
    return result_df
