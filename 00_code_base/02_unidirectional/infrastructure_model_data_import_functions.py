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
import os

#define function

def load_input_data(file_directory, file_name):
    """
    Load data from an Excel file and return the corresponding DataFrames.

    Parameters:
    file_directory (str): The path to the directory containing the Excel file.
    file_name (str): The name of the Excel file.

    Returns:
    tuple: A tuple containing the following DataFrames:
        - df_nodes
        - df_commodities
        - df_edges
        - df_parameter
        - df_supply_values
    """
    # Construct full file path
    input_file_path = os.path.join(file_directory, file_name)
    full_input_path = os.path.abspath(os.path.join(os.getcwd(), input_file_path))

    # Read the Excel file into DataFrames
    df_nodes = pd.read_excel(full_input_path, sheet_name='Nodes')
    df_commodities = pd.read_excel(full_input_path, sheet_name='Commodities')
    df_edges = pd.read_excel(full_input_path, sheet_name='Edges')
    df_parameter = pd.read_excel(full_input_path, sheet_name='Parameters')
    df_supply_values = pd.read_excel(full_input_path, sheet_name='Supply')

    return df_nodes, df_commodities, df_edges, df_parameter, df_supply_values


def extract_network_data(df_nodes, df_commodities, df_edges, df_parameter, df_supply_values):
    # Extract nodes, edges, and commodities
    network_nodes = df_nodes['Nodes'].dropna().tolist()
    commodities = df_commodities['Commodities'].dropna().tolist()
    edges = list(zip(df_edges['Source'], df_edges['Destination']))

    # Create a nested dictionary for initial capacities
    initial_capacities = {}
    for index, row in df_parameter.iterrows():
        commodity = row['Commodity']
        source = row['Source']
        destination = row['Destination']
        initial_capacity = row['initial_capacities']

        edge = f"{source}{destination}"

        if commodity not in initial_capacities:
            initial_capacities[commodity] = {}

        initial_capacities[commodity][edge] = initial_capacity

    # Create a nested dictionary for max capacities
    max_capacities = {}
    for index, row in df_parameter.iterrows():
        commodity = row['Commodity']
        source = row['Source']
        destination = row['Destination']
        max_capacity = row['max_capacities']

        edge = f"{source}{destination}"

        if commodity not in max_capacities:
            max_capacities[commodity] = {}

        max_capacities[commodity][edge] = max_capacity

    # Create a nested dictionary for edge cost
    edge_cost = {}
    for index, row in df_parameter.iterrows():
        commodity = row['Commodity']
        source = row['Source']
        destination = row['Destination']
        cost = row['costs_edge']

        edge = f"{source}{destination}"

        if commodity not in edge_cost:
            edge_cost[commodity] = {}

        edge_cost[commodity][edge] = cost

    # Create a nested dictionary for new pipeline costs
    pipe_new_cost = {}
    for index, row in df_parameter.iterrows():
        commodity = row['Commodity']
        source = row['Source']
        destination = row['Destination']
        new_cost = row['new_build_cost']

        edge = f"{source}{destination}"

        if commodity not in pipe_new_cost:
            pipe_new_cost[commodity] = {}

        pipe_new_cost[commodity][edge] = new_cost

    # Create a nested dictionary for pipeline conversion costs
    pipe_conv_cost = {}
    for index, row in df_parameter.iterrows():
        commodity = row['Commodity']
        source = row['Source']
        destination = row['Destination']
        conv_cost = row['conversion_cost']

        edge = f"{source}{destination}"

        if commodity not in pipe_conv_cost:
            pipe_conv_cost[commodity] = {}

        pipe_conv_cost[commodity][edge] = conv_cost

    # Create a nested dictionary for pipeline conversion capacity factor
    pipe_conv_factor = {}
    for index, row in df_parameter.iterrows():
        commodity = row['Commodity']
        source = row['Source']
        destination = row['Destination']
        conv_cap_factor = row['conversion_capacity_factor']

        edge = f"{source}{destination}"

        if commodity not in pipe_conv_factor:
            pipe_conv_factor[commodity] = {}

        pipe_conv_factor[commodity][edge] = conv_cap_factor

    # Create a nested dictionary for supply values, skipping 0 and NaN values
    supply_values = {}
    for index, row in df_supply_values.iterrows():
        commodity = row['Commodity']
        supply_node = row['Node']
        supply_value = row['Supply']

        if commodity not in supply_values:
            supply_values[commodity] = {}

        # Skip 0 and NaN values
        if not pd.isna(supply_value) and supply_value != 0:
            supply_values[commodity][supply_node] = supply_value

    # Create a nested dictionary for node values, skipping 0 and NaN values
    node_values = {}
    for index, row in df_supply_values.iterrows():
        commodity = row['Commodity']
        demand_node = row['Node']
        node_value = row['Supply']

        if commodity not in node_values:
            node_values[commodity] = {}

        # Skip NaN values
        if not pd.isna(node_value):
            node_values[commodity][demand_node] = node_value

    return (
        network_nodes, commodities, edges, initial_capacities, 
        max_capacities, edge_cost, pipe_new_cost, pipe_conv_cost, 
        pipe_conv_factor, supply_values, node_values
        )

def create_initial_capacities_separator_dict(df_parameter):
    # Create a nested dictionary for initial capacities with edges separated by commas
    initial_capacities_data = {}

    # Iterate over the rows of the DataFrame
    for index, row in df_parameter.iterrows():
        commodity = row['Commodity']
        source = row['Source']
        destination = row['Destination']
        initial_capacity = row['initial_capacities']

        # Define the edge as a string with source and destination
        edge = f"{source},{destination}"

        # Check if the commodity already exists in the dictionary, if not, initialize it
        if commodity not in initial_capacities_data:
            initial_capacities_data[commodity] = {}

        # Assign the initial capacity to the corresponding edge
        initial_capacities_data[commodity][edge] = initial_capacity

    return initial_capacities_data