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
import networkx as nx

#define function

def create_slack_nodes_and_links(node_values, commodities, methane_value=10000000, hydrogen_value=10000000):
    # Create a new dictionary for positive values
    positive_values_dict = {}

    # Iterate through the outer dictionary
    for node, values in node_values.items():
        # Filter out positive values from the inner dictionary
        positive_values = {key: value for key, value in values.items() if value > 0}

        # Check if there are positive values before adding to the new dictionary
        if positive_values:
            positive_values_dict[node] = positive_values

    # Get all keys from the inner dictionaries
    all_keys = [key for values in positive_values_dict.values() for key in values.keys()]

    # Remove duplicates to get unique keys
    unique_keys = list(set(all_keys))

    # Create a list with names "shortage_" followed by each key
    shortage_list = [f'shortage_{key}' for key in unique_keys]

    # Create shortage edges list, linking shortage nodes to supply nodes
    shortage_edges_list = [(key, shortage) for key, shortage in zip(shortage_list, unique_keys)]

    # Create a dictionary for capacities of shortage nodes (with infinite capacity represented by a high value)
    shortage_capacity_dict = {commodity: {f'{key}{shortage}': 10000000 for key, shortage in zip(shortage_list, unique_keys)} 
                              for commodity in commodities}

    # Create a dictionary for cost of shortage nodes (with a high cost for infinite capacity)
    shortage_cost_dict = {
        'Methane': {f'{key}{shortage}': methane_value for key, shortage in zip(shortage_list, unique_keys)},
        'Hydrogen': {f'{key}{shortage}': hydrogen_value for key, shortage in zip(shortage_list, unique_keys)}
    }

    # Returning the components individually
    return shortage_list, shortage_edges_list, shortage_capacity_dict, shortage_cost_dict

def create_excess_nodes_for_supply(node_values, commodities, methane_value=0, hydrogen_value=10000000):
    # Create a new dictionary for positive values (representing supply)
    positive_values_dict = {}

    # Iterate through the outer dictionary (supply nodes)
    for node, values in node_values.items():
        # Filter out positive values from the inner dictionary (representing supply of commodities)
        positive_values = {key: value for key, value in values.items() if value > 0}

        # If there are positive values, add the node and its positive values to the dictionary
        if positive_values:
            positive_values_dict[node] = positive_values

    # Get all unique commodity keys across all supply nodes
    all_keys = [key for values in positive_values_dict.values() for key in values.keys()]
    unique_keys = list(set(all_keys))  # Remove duplicates to get unique commodities

    # Create a list of "excess_{commodity}" names
    excess_list = [f'{key}_excess' for key in unique_keys]

    # Create excess edges list, linking excess nodes to each supply node
    excess_edges_list = [(excess, key) for key, excess in zip(excess_list, unique_keys)]

    # Create a dictionary for excess node capacities (infinite capacity with a high value, e.g., 10000)
    excess_capacity_dict = {
        commodity: {f'{excess}{key}': 1000000 for key, excess in zip(excess_list, unique_keys)}
        for commodity in commodities
    }

    # Create a dictionary for excess node costs (no cost for methane, high cost for hydrogen)
    excess_cost_dict = {
        'Methane': {f'{excess}{key}': methane_value for key, excess in zip(excess_list, unique_keys)},
        'Hydrogen': {f'{excess}{key}': hydrogen_value for key, excess in zip(excess_list, unique_keys)}
    }

    # Returning the components individually
    return excess_list, excess_edges_list, excess_capacity_dict, excess_cost_dict

def check_graph_connectivity(edges):
    # Create a graph and add edges
    G = nx.Graph()
    G.add_edges_from(edges)
    
    # Check if the graph is connected
    if nx.is_connected(G):
        print("The graph is connected.")
    else:
        print("The graph is not connected.")


def check_graph_connectivity_and_components(edges):
    # Create a graph and add edges
    G = nx.Graph()
    G.add_edges_from(edges)
    
    # Get connected components
    connected_components = list(nx.connected_components(G))
    
    # Check if the graph is connected
    if len(connected_components) == 1:
        print("The graph is connected.")
    else:
        print("The graph is not connected.")
        print("Connected components:")
        for i, component in enumerate(connected_components):
            print(f"Component {i+1}: {component}")

def check_if_all_nodes_connected(network_nodes, edges):
    # Create a graph and add edges
    G = nx.Graph()
    G.add_edges_from(edges)
    
    # Get connected components
    connected_components = list(nx.connected_components(G))
    
    # Check if all nodes are in one connected component
    if any(set(network_nodes) == component for component in connected_components):
        print("All nodes are connected.")
    else:
        print("Not all nodes are connected.")
        
        # Find nodes that are not connected
        connected_nodes = set(node for component in connected_components for node in component)
        not_connected_nodes = set(network_nodes) - connected_nodes
        
        # Print the nodes that are not connected
        if not_connected_nodes:
            print("Not connected nodes:", not_connected_nodes)
        else:
            print("All nodes are connected.")