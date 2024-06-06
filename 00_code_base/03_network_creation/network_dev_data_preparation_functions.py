'''
This is the network development of CSEI, an Open-source Tool
for investigating the development of infrastrucutre. The focus of the tool is on
the development of the hydrogen infrastructure. 
The tool is developed at the Copenhagen School of
Energy Infrastructure at the Copenhagen Business School.
---------------------------------------
Functions File for Data Prep:
The functions include the logical prossecing, mathematical calculation
logic for the preparation of the input data file for the model runs.
SPDX-FileCopyrightText: Johannes Giehl <jfg.eco@cbs.dk>
SPDX-License-Identifier: GNU GENERAL PUBLIC LICENSE GPL 3.0
'''

'''Import packages'''
import numpy as np
import pandas as pd

'''Define functions'''

def generate_parallel_connections(input_df):
    result_rows = []
    created_nodes = {}

    for _, row in input_df.iterrows():
        source_name = row['source_name']
        target_name = row['target_name']
        occurrences = row['occurrences']

        # Check if the target node has already been created
        start_index = created_nodes.get(target_name, 0) + 1

        for i in range(start_index, occurrences + start_index):
            new_target = f"{target_name}_{i}"
            result_rows.append({'source_name': source_name, 'target_name': new_target})

            # Add a source node targeting the original target node
            result_rows.append({'source_name': new_target, 'target_name': target_name})

            # Update the created nodes dictionary
            created_nodes[target_name] = i

    result_df = pd.DataFrame(result_rows)

    return result_df

def replace_nan_with_value(dataframe, column_name, replacement_value):
    """
    Replace all NaN values in a specific column of a DataFrame with a given value.

    Parameters:
        dataframe (pd.DataFrame): The input DataFrame.
        column_name (str): The name of the column in which NaN values should be replaced.
        replacement_value: The value to replace NaN with.

    Returns:
        pd.DataFrame: A new DataFrame with NaN values replaced in the specified column.
    """
    dataframe.fillna({column_name: replacement_value}, inplace=True)
    return dataframe

# Function to append the counter to duplicate indices
def handle_duplicates(index, occurrence_counter, counter):
    if occurrence_counter[index] > 1:
        counter[index] += 1
        return f"{index}_{counter[index]}"
    else:
        return index