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