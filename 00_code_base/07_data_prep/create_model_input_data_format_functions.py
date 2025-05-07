'''
This is the gas and hydrogen infrastructure of CSEI, an open-source Tool
for analyzing different aspects of the infrastructure. Examples are the 
development, including the conversion of the natural gas to a hydrogen grid, 
or the supply situation in Europe. The tool is developed at the Copenhagen 
School of Energy Infrastructure at the Copenhagen Business School.
---------------------------------------
Functions File for the preparation of the input data structure:
The functions include the logical prossecing, mathematical calculation
logic for the preparation of the input data file for the model runs.
SPDX-FileCopyrightText: Johannes Giehl <jfg.eco@cbs.dk>
SPDX-License-Identifier: GNU GENERAL PUBLIC LICENSE GPL 3.0
'''

# import packages
import pandas as pd
import os

# Function to calculate cost
def calculate_cost_vectorized(df, cost_factor_transportation, cost_factor_suez, cost_factor_panama):
    # Start with base transportation cost
    cost = df['Distance [km]'] * cost_factor_transportation

    # Add Suez and Panama surcharges where applicable
    with_suez = df['Suez or Panama'].str.contains('Suez', na=False) & (df['Distance [km]'] > 0)
    with_panama = df['Suez or Panama'].str.contains('Panama', na=False) & (df['Distance [km]'] > 0)

    cost += with_suez * (cost_factor_suez / df['Distance [km]'])
    cost += with_panama * (cost_factor_panama / df['Distance [km]'])

    return cost

# Function to create the new dataframe based on the "From" column for liquefaction cost
def create_LNG_liquefaction_df(df, factor):
    # Step 1: Create a new dataframe with unique "From" values and the corresponding "To" column
    unique_from_df = pd.DataFrame(df['From'].unique(), columns=['From'])
    
    # Step 2: Adjust the "From" column by removing "_LNG" and place the original "From" values in the "To" column
    unique_from_df['To'] = unique_from_df['From']
    unique_from_df['From'] = unique_from_df['From'].str.replace('_LNG_exp', '')
    
    # Step 3: Add the "Cost" column with the value of cost_factor_liquification
    unique_from_df['Cost'] = factor
    
    return unique_from_df

# Function to create the new dataframe based on the "To" column for regasification cost
def create_LNG_regasification_df(df, factor):
    # Step 1: Create a new dataframe with unique "To" values and the corresponding "To" column
    unique_from_df = pd.DataFrame(df['To'].unique(), columns=['To'])
    
    # Step 2: Adjust the "To" column by removing "_LNG" and place the original "To" values in the "From" column
    unique_from_df['From'] = unique_from_df['To']
    unique_from_df['To'] = unique_from_df['To'].str.replace('_LNG_imp', '')
    
    # Step 3: Add the "Cost" column with the value of cost_factor_liquification
    unique_from_df['Cost'] = factor
    
    return unique_from_df

#Define a function to multiply the distance by a cost factor for the pipelines
def pipeline_transport_cost(df, cost_factor):
    df["Cost"] = df["distance [km]"] * cost_factor
    return df

# Function to create df_supply_demand_global
def create_supply_demand_df(df, supply=True):
    # Create the new dataframe with required columns
    df_supply_demand_global = pd.DataFrame({
        'Commodity': ['Methane'] * len(df),  # Set 'Methane' for all rows
        'Node': df['Country'] + ('_Prod' if supply else ''),  # Append '_Prod' if supply is True
        'Supply': df['GWh [2020]']  # Use 'GWh [2020]' for supply
    })
    
    return df_supply_demand_global

def expand_with_hydrogen(df, hydrogen_investment):
    if hydrogen_investment:
        return df  # If investment is allowed, return the original dataframe unchanged

    # Check if the input dataframe follows the (Commodity, Source, Destination) structure
    if {'Commodity', 'Source', 'Destination'}.issubset(df.columns):
        # Copy relevant columns and create a hydrogen version
        hydrogen_df = df[['Commodity', 'Source', 'Destination']].copy()
        hydrogen_df['Commodity'] = 'Hydrogen'  # Replace Commodity with Hydrogen
        
    # If the input dataframe follows the (Commodity, Node, Supply) structure
    elif {'Commodity', 'Node', 'Supply'}.issubset(df.columns):
        # Copy relevant columns and create a hydrogen version
        hydrogen_df = df[['Commodity', 'Node']].copy()
        hydrogen_df['Commodity'] = 'Hydrogen'  # Replace Commodity with Hydrogen
    
    else:
        raise ValueError("Unexpected dataframe format. Must contain either ['Commodity', 'Source', 'Destination'] or ['Commodity', 'Node', 'Supply']")

    # Fill all other columns with 0
    for col in df.columns:
        if col not in hydrogen_df.columns:  # Skip the required columns
            hydrogen_df[col] = 0

    # Combine the original dataframe with the new hydrogen dataframe
    df_expanded = pd.concat([df, hydrogen_df], ignore_index=True)

    return df_expanded

def integrate_pipeline_costs(df_pipelines, df_transport_cost):
    """
    Merges transport cost data into the pipeline dataframe based on matching From-To relationships, 
    considering both directions (From->To and To->From).
    
    Parameters:
        df_pipelines (pd.DataFrame): DataFrame containing pipeline capacities.
        df_transport_cost (pd.DataFrame): DataFrame containing transport distances and costs.
        
    Returns:
        pd.DataFrame: Updated pipeline DataFrame with an additional 'cost' column.
    """
    # Create reversed pairs for bidirectional matching (From -> To and To -> From)
    df_reversed = df_transport_cost.rename(columns={'From': 'To', 'To': 'From', 'Cost': 'Cost_reversed'})
    
    # Concatenate original and reversed cost data to handle both directions
    df_cost = pd.concat([df_transport_cost[['From', 'To', 'Cost']], df_reversed[['From', 'To', 'Cost_reversed']]], ignore_index=True)
    
    # Merge the concatenated cost data with df_pipelines to get the corresponding cost
    df_pipelines = df_pipelines.merge(
        df_cost, 
        on=['From', 'To'], 
        how='left'
    )
    
    # For cases where the reverse relation exists, use the reversed cost value
    df_pipelines['Cost'] = df_pipelines['Cost'].fillna(df_pipelines['Cost_reversed'])

    # Drop the extra reversed cost column (no longer needed)
    df_pipelines = df_pipelines.drop(columns=['Cost_reversed'])
    
    return df_pipelines

def extract_unique_nodes(df):
    unique_nodes = pd.unique(df[['Source', 'Destination']].values.ravel())
    return pd.DataFrame({'Nodes': unique_nodes})


def create_base_edges(df):
    """Create a dataframe with unique (From, To) pairs."""
    unique_pairs = set((row['From'], row['To']) for _, row in df.iterrows())
    return pd.DataFrame(unique_pairs, columns=['Source', 'Destination'])

#function to generate structure of European pipeline parameters
def process_european_pipeline_edges(df_pipelines_europe):
    """Process European pipeline transport cost and capacity data."""
    df_pipelines = create_base_edges(df_pipelines_europe)

    # Merge cost & capacity
    df_pipelines = df_pipelines.merge(
        df_pipelines_europe[['From', 'To', 'Cost', 'GWh/a']],
        left_on=['Source', 'Destination'],
        right_on=['From', 'To'],
        how='left'
    ).drop(columns=['From', 'To']).rename(columns={'Cost': 'costs_edge', 'GWh/a': 'Capacity_pipelines'})

    # Default values for missing capacities
    df_pipelines['initial_capacities'] = df_pipelines['Capacity_pipelines'].fillna(999999999)
    df_pipelines['max_capacities'] = df_pipelines['initial_capacities']
    df_pipelines = df_pipelines.drop(columns=['Capacity_pipelines'])

    # Add default columns
    df_pipelines.insert(0, 'Commodity', 'Methane')
    df_pipelines['new_build_cost'] = 1000000
    df_pipelines['conversion_cost'] = 0
    df_pipelines['conversion_capacity_factor'] = 1

    column_to_move = df_pipelines.pop("costs_edge")

    # insert column with insert(location, column_name, column_value)
    df_pipelines.insert(5, "costs_edge", column_to_move)

    return df_pipelines

#process LNG import function (for European import capacities)
def process_LNG_import_edges(df_LNG_europe):
    """Process LNG import terminal costs and capacities."""
    df_LNG = create_base_edges(df_LNG_europe)

    df_LNG = df_LNG.merge(
        df_LNG_europe[['From', 'To', 'Cost', 'GWh/a']],
        left_on=['Source', 'Destination'],
        right_on=['From', 'To'],
        how='left'
    ).drop(columns=['From', 'To']).rename(columns={'Cost': 'costs_edge', 'GWh/a': 'Capacity_LNG_import'})

    df_LNG['initial_capacities'] = df_LNG['Capacity_LNG_import'].fillna(999999999)
    df_LNG['max_capacities'] = df_LNG['initial_capacities']
    df_LNG = df_LNG.drop(columns=['Capacity_LNG_import'])

    # Add default columns
    df_LNG.insert(0, 'Commodity', 'Methane')
    df_LNG['new_build_cost'] = 1000000
    df_LNG['conversion_cost'] = 0
    df_LNG['conversion_capacity_factor'] = 1

    column_to_move = df_LNG.pop("costs_edge")

    # insert column with insert(location, column_name, column_value)
    df_LNG.insert(5, "costs_edge", column_to_move)

    return df_LNG

#function to process LNG global exchange parameters for the edges
def process_LNG_global_edges(df_LNG_global):
    """Process global LNG transport costs and capacities."""
    df_LNG_global_processed = create_base_edges(df_LNG_global)

    # Merge cost and distance data
    df_LNG_global_processed = df_LNG_global_processed.merge(
        df_LNG_global[['From', 'To', 'Cost', 'GWh/a']],
        left_on=['Source', 'Destination'],
        right_on=['From', 'To'],
        how='left'
    ).drop(columns=['From', 'To']).rename(columns={'Cost': 'costs_edge', 'GWh/a': 'Capacity_LNG_global'})

    # Handle capacity values
    df_LNG_global_processed['initial_capacities'] = df_LNG_global_processed['Capacity_LNG_global'].fillna(999999999)
    df_LNG_global_processed['max_capacities'] = df_LNG_global_processed['initial_capacities']
    df_LNG_global_processed = df_LNG_global_processed.drop(columns=['Capacity_LNG_global'])

    # Add default columns
    df_LNG_global_processed.insert(0, 'Commodity', 'Methane')
    df_LNG_global_processed['new_build_cost'] = 1000000
    df_LNG_global_processed['conversion_cost'] = 0
    df_LNG_global_processed['conversion_capacity_factor'] = 1

    # Move `costs_edge` column to the correct position
    column_to_move = df_LNG_global_processed.pop("costs_edge")
    df_LNG_global_processed.insert(5, "costs_edge", column_to_move)

    return df_LNG_global_processed


def process_LNG_regasification_edges(df_LNG_regasification):
    """Process LNG regasification costs."""
    df_regas = create_base_edges(df_LNG_regasification)

    df_regas = df_regas.merge(
        df_LNG_regasification[['From', 'To', 'Cost']],
        left_on=['Source', 'Destination'],
        right_on=['From', 'To'],
        how='left'
    ).drop(columns=['From', 'To']).rename(columns={'Cost': 'costs_edge'})

        # Default values for missing capacities
    df_regas['initial_capacities'] = 999999999
    df_regas['max_capacities'] = df_regas['initial_capacities']

    # Add default columns
    df_regas.insert(0, 'Commodity', 'Methane')
    df_regas['new_build_cost'] = 1000000
    df_regas['conversion_cost'] = 0
    df_regas['conversion_capacity_factor'] = 1

    column_to_move = df_regas.pop("costs_edge")

    # insert column with insert(location, column_name, column_value)
    df_regas.insert(5, "costs_edge", column_to_move)
    
    return df_regas


#function to create parameters for liquification nodes
def process_LNG_liquefaction_edges(df_LNG_liquefaction):
    """Process LNG liquefaction costs."""
    df_liquefaction = create_base_edges(df_LNG_liquefaction)

    df_liquefaction = df_liquefaction.merge(
        df_LNG_liquefaction[['From', 'To', 'Cost']],
        left_on=['Source', 'Destination'],
        right_on=['From', 'To'],
        how='left'
    ).drop(columns=['From', 'To']).rename(columns={'Cost': 'costs_edge'})

    # Default values for missing capacities
    df_liquefaction['initial_capacities'] = 999999999
    df_liquefaction['max_capacities'] = df_liquefaction['initial_capacities']

    # Add default columns
    df_liquefaction.insert(0, 'Commodity', 'Methane')
    df_liquefaction['new_build_cost'] = 1000000
    df_liquefaction['conversion_cost'] = 0
    df_liquefaction['conversion_capacity_factor'] = 1

    column_to_move = df_liquefaction.pop("costs_edge")

    # insert column with insert(location, column_name, column_value)
    df_liquefaction.insert(5, "costs_edge", column_to_move)

    return df_liquefaction

#function to create parameters for global pipelines
def process_global_pipeline_edges(df_global_pipe_transport_cost):
    """Process global pipeline transport costs."""
    df_global_pipeline = create_base_edges(df_global_pipe_transport_cost)

    df_global_pipeline = df_global_pipeline.merge(
        df_global_pipe_transport_cost[['From', 'To', 'Cost', 'GWh/a']],
        left_on=['Source', 'Destination'],
        right_on=['From', 'To'],
        how='left'
    ).drop(columns=['From', 'To']).rename(columns={'Cost': 'costs_edge', 'GWh/a': 'Capacity_pipelines'})

    # Default values for missing capacities
    df_global_pipeline['initial_capacities'] = df_global_pipeline['Capacity_pipelines'].fillna(9999)
    df_global_pipeline['max_capacities'] = df_global_pipeline['initial_capacities']
    df_global_pipeline = df_global_pipeline.drop(columns=['Capacity_pipelines'])

    # Add default columns
    df_global_pipeline.insert(0, 'Commodity', 'Methane')
    df_global_pipeline['new_build_cost'] = 1000000
    df_global_pipeline['conversion_cost'] = 0
    df_global_pipeline['conversion_capacity_factor'] = 1

    column_to_move = df_global_pipeline.pop("costs_edge")

    # insert column with insert(location, column_name, column_value)
    df_global_pipeline.insert(5, "costs_edge", column_to_move)

    return df_global_pipeline

def remove_existing_LNG_edges(df_regasification_LNG_edges, df_europe_LNG_edges):
    """Removes rows from df_regasification_LNG_edges if the Source-Destination pair exists in df_europe_LNG_edges."""
    existing_edges = set(zip(df_europe_LNG_edges['Source'], df_europe_LNG_edges['Destination']))
    
    df_filtered = df_regasification_LNG_edges[
        ~df_regasification_LNG_edges.apply(lambda row: (row['Source'], row['Destination']) in existing_edges, axis=1)
    ]
    
    return df_filtered

#function to create connections from missing Countries to LNG export connections
def ensure_direct_connections(df, df_LNG_europe, cost_factor_liquefaction):
    # Ensure no NaN values in 'Source' and create a new dataframe
    df_cleaned = df.dropna(subset=["Source"]).copy()

    # Extract all LNG sources from df_edges_cap_cost
    lng_sources = set(df_cleaned[df_cleaned["Source"].astype(str).str.endswith("_LNG")]["Source"])

    # Extract LNG sources that should be **excluded** (those in df_LNG_europe["From"])
    excluded_lng_sources = set(df_LNG_europe["From"].dropna().unique())

    # Keep only LNG sources that **should be considered**
    valid_lng_sources = lng_sources - excluded_lng_sources

    # Extract base country codes that need new connections
    base_countries = {src.replace("_LNG", "") for src in valid_lng_sources}

    # Initialize a list to collect missing rows
    missing_rows = []

    # Create the missing connections for the countries in base_countries
    for country in base_countries:
        source = country
        destination = f"{country}_LNG"

        # Ensure this direct connection doesn't already exist
        if not ((df_cleaned["Source"] == source) & (df_cleaned["Destination"] == destination)).any():
            missing_rows.append({
                "Commodity": "Methane",
                "Source": source,
                "Destination": destination,
                "initial_capacities": 999999999,
                "max_capacities": 999999999,
                "costs_edge": cost_factor_liquefaction,
                "new_build_cost": 1000000,
                "conversion_cost": 0,
                "conversion_capacity_factor": 1
            })

    # Create a new dataframe for the missing rows and return it
    df_missing = pd.DataFrame(missing_rows)

    return df_missing

#create edges for the production nodes of each country
def create_Production_node_edges(df_demand_supply_complete, production_cost_df):
    # Ensure the 'Node' column is treated as a string
    df_demand_supply_complete['Node'] = df_demand_supply_complete['Node'].astype(str)
    
    # Merge the supply-demand dataframe with the production cost dataframe on the 'Node' column
    df_with_costs = pd.merge(df_demand_supply_complete, production_cost_df, left_on='Node', right_on='Node', how='left')

    # Initialize an empty list to collect the rows for the new dataframe
    new_rows = []

    # Loop through the rows in the merged dataframe
    for _, row in df_with_costs.iterrows():
        node = row['Node']

        # Check if the node ends with "_Prod"
        if node.endswith("_Prod"):
            source = node
            destination = node.replace("_Prod", "")  # Remove "_Prod" from the node to get the destination

            # Get the production cost for this node from the merged dataframe
            production_cost = row['Cost']  # Assuming the production cost is in the 'Cost' column

            # Create a new row for the production connection with the known dummy values
            new_rows.append({
                "Commodity": row['Commodity'],  # Assuming it's "Methane" from the example
                "Source": source,
                "Destination": destination,
                "initial_capacities": 999999999,  # Dummy value
                "max_capacities": 999999999,  # Dummy value
                "costs_edge": production_cost,  # Use the production cost from the dataframe
                "new_build_cost": 1000000,  # Dummy value
                "conversion_cost": 0,  # Dummy value
                "conversion_capacity_factor": 1  # Dummy value
            })

    # Create a new dataframe from the collected rows
    df_Prod_edges = pd.DataFrame(new_rows)

    return df_Prod_edges

#function to remove countries that are not part of the analyses/model
def remove_rows_containing_strings(df, string_list):
    return df[
        ~df.apply(
            lambda row: row.astype(str)
                        .str.contains('|'.join(string_list), case=False, na=False)
                        .any(), 
            axis=1
        )
    ]

#add missing information to the demand and supply information but with value 0
def create_missing_prod_and_lng_nodes(df_demand_supply_complete, LNG_countries_list):
    # Step 1: Create missing _Prod nodes (but not for nodes already having _LNG)
    new_prod_nodes = []
    for node in df_demand_supply_complete['Node']:
        if not node.endswith("_Prod") and not node.endswith("_LNG"):
            prod_node = f"{node}_Prod"
            if prod_node not in df_demand_supply_complete['Node'].values:
                new_prod_nodes.append({
                    "Commodity": "Methane",
                    "Node": prod_node,
                    "Supply": 0
                })
    
    # Step 2: Create missing _LNG_export nodes
    new_lng_export_nodes = []
    for node in df_demand_supply_complete['Node']:
        country_code = node.split('_')[0]
        if not node.endswith("_Prod") and not node.endswith("_LNG_exp") and not node.endswith("_LNG_imp") and country_code in LNG_countries_list:
            new_lng_export_nodes.append({
                "Commodity": "Methane",
                "Node": f"{node}_LNG_exp",
                "Supply": 0
            })

    # Step 2: Create missing _LNG_import nodes
    new_lng_import_nodes = []
    for node in df_demand_supply_complete['Node']:
        country_code = node.split('_')[0]
        if not node.endswith("_Prod") and not node.endswith("_LNG_exp") and not node.endswith("_LNG_imp") and country_code in LNG_countries_list:
            new_lng_import_nodes.append({
                "Commodity": "Methane",
                "Node": f"{node}_LNG_imp",
                "Supply": 0
            })
    
    # Convert new nodes lists to DataFrames
    df_new_prod_nodes = pd.DataFrame(new_prod_nodes)
    df_new_lng_export_nodes = pd.DataFrame(new_lng_export_nodes)
    df_new_lng_import_nodes = pd.DataFrame(new_lng_import_nodes)

    # Combine both DataFrames
    df_new_nodes = pd.concat([df_new_prod_nodes, df_new_lng_export_nodes, df_new_lng_import_nodes], ignore_index=True)

    # Return new nodes dataframe
    return df_new_nodes

#combine all df for the supply inpput sheet (demand (negative) or supply (positive) values
def add_missing_supply_nodes(df_demand_supply_complete, df_missing_supply_values_for_nodes):
    # Merge on 'Commodity' and 'Node', keeping existing values in df_demand_supply_complete
    df_combined = pd.concat([df_demand_supply_complete, df_missing_supply_values_for_nodes]) \
                    .drop_duplicates(subset=['Commodity', 'Node'], keep='first') \
                    .reset_index(drop=True)
    return df_combined

def extract_unique_commodities(df_demand_supply_complete):
    unique_commodities = df_demand_supply_complete['Commodity'].unique()
    return pd.DataFrame({'Commodities': unique_commodities})

def merge_all_edges(*dfs):
    """
    Merges multiple edge dataframes while removing duplicate Source-Destination pairs.
    
    Args:
        *dfs: Any number of dataframes to be merged.
    
    Returns:
        A merged dataframe with duplicates removed.
    """
    # Step 1: Concatenate all dataframes
    df_merged = pd.concat(dfs, ignore_index=True)

    # Step 2: Remove duplicate edges (keeping the first occurrence)
    df_merged = df_merged.drop_duplicates(subset=['Source', 'Destination'], keep='first')

    return df_merged

def update_parameter(df_edges_complete, df_updates, parameter_name, update_column):
    """
    Updates the specified parameter in df_edges_complete based on df_updates.

    Parameters:
    df_edges_complete (pd.DataFrame): Original dataframe with edges and costs.
    df_updates (pd.DataFrame): DataFrame containing updates with 
                               Commodity, Source, Destination, and new values.
    parameter_name (str): The name of the column to update in df_edges_complete.
    update_column (str): The name of the column in df_updates that contains new values.

    Returns:
    pd.DataFrame: Updated df_edges_complete with modified parameter values.
    """
    # Rename the update column to match parameter_name for easier merging
    df_updates = df_updates.rename(columns={update_column: parameter_name})
    
    # Merge the two dataframes on Commodity, Source, and Destination
    df_updated = df_edges_complete.merge(
        df_updates, 
        on=["Commodity", "Source", "Destination"], 
        how="left", 
        suffixes=("", "_update")
    )
    
    # Update the specified parameter where new values exist
    df_updated[parameter_name] = df_updated[f"{parameter_name}_update"].combine_first(df_updated[parameter_name])
    
    # Drop the temporary column
    df_updated.drop(columns=[f"{parameter_name}_update"], inplace=True)
    
    return df_updated

def update_investment_cost(df_updates_invest, df_distances):
    """
    Updates 'costs_new' in df_updates_invest by multiplying it with the corresponding
    'distance [km]' from df_distances, treating reversed Source-Destination pairs as equivalent.

    Parameters:
    - df_updates_invest (pd.DataFrame): ['Commodity', 'Source', 'Destination', 'costs_new', 'limit_new']
    - df_distances (pd.DataFrame): ['from', 'to', 'distance [km]',  'Cost']

    Returns:
    - pd.DataFrame: same as df_updates_invest, with 'costs_new' updated
    """

    # Create route keys
    distance_dict = {
        tuple(sorted([row['From'], row['To']])): row['distance [km]']
        for _, row in df_distances.iterrows()
    }

    # Update costs_new by multiplying with corresponding distance
    def apply_distance(row):
        key = tuple(sorted([row['Source'], row['Destination']]))
        distance = distance_dict.get(key)
        return row['costs_new'] * distance if distance is not None else row['costs_new']

    df_updated = df_updates_invest.copy()
    df_updated['costs_new'] = df_updated.apply(apply_distance, axis=1)

    return df_updated