# import packages
import pandas as pd


#define functions
def get_scenario_suffix(scenario):
    """
    Converts 'ESR_2026_run_2021' -> '2021'
    Converts 'ESR_2026_run_2024_plus_no_QA' -> '2024_plus_no_QA'
    """
    return scenario.replace('ESR_2026_run_', '', 1)


def extract_scenario_names(df_names_demand, df_names_shares):
    """
    Extracts scenario names from lists of dataframe names by removing prefixes.

    Parameters:
    - input_names: list of strings (e.g. ['inputs_ESR_2026_run_2021', ...])
    - share_names: list of strings (e.g. ['costs_shares_ESR_2026_run_2021', ...])

    Returns:
    - sorted list of unique scenario names
    """

    def clean_name(name):
        if name.startswith('inputs_'):
            return name.replace('inputs_', '', 1)
        elif name.startswith('costs_shares_'):
            return name.replace('costs_shares_', '', 1)
        return name

    scenarios = set()

    for name in df_names_demand:
        scenarios.add(clean_name(name))

    for name in df_names_shares:
        scenarios.add(clean_name(name))

    return sorted(scenarios)


def filter_negative_supply(df, commodity_name):
    """
    Filters the DataFrame to a given commodity and removes rows with Supply >= 0.
    Handles column name capitalization issues.
    """
    # Standardize column names (optional safety step)
    df = df.rename(columns={col: col.strip().capitalize() for col in df.columns})
    
    # Check for required columns
    required_columns = {'Commodity', 'Node', 'Supply'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Missing required columns. Found columns: {df.columns.tolist()}")

    # Filter and return
    df_filtered = df[(df['Commodity'] == commodity_name) & (df['Supply'] < 0)].copy()

    # make values now positive for later emissions calculations
    df_filtered['Supply'] = df_filtered['Supply'] * -1  
    
    return df_filtered.reset_index(drop=True)

def calculate_emissions_per_country(emission_factors, supply_shares, demand):
    # Extract country/region code before the first underscore (supports 2- or 3-letter codes)
    supply_shares['Source'] = supply_shares['Origin'].str.extract(r'^([A-Z]+)_')

    # Merge with demand
    df = supply_shares.merge(demand, on='Node')

    # Safe lookup for emission factors with fallback to 0
    def get_factor(node, source):
        try:
            return emission_factors.at[node, source]
        except KeyError:
            return 0

    # Calculate emission factor and emissions
    df['EmissionFactor'] = df.apply(lambda row: get_factor(row['Node'], row['Source']), axis=1)
    df['Emissions'] = df['Supply'] * df['Share'] * df['EmissionFactor']

    # Aggregate emissions per demand country
    return df.groupby('Node')['Emissions'].sum().reset_index()

def calculate_domestic_emissions(dfs_emission_factors_dom, supply_shares, supply_df):
    """
    Calculates emissions from domestic production only.
    
    Parameters:
    - supply_shares: DataFrame with 'Node', 'Origin', 'Share'
    - supply_df: DataFrame with 'Node', 'Supply' (positive values)
    - dfs_emission_factors_dom: DataFrame with index = 'Node', column = 'Factor'
    
    Returns:
    - DataFrame with 'Node' and 'Domestic_Emissions'
    """
    # Extract Source country code from Origin
    supply_shares['Source'] = supply_shares['Origin'].str.extract(r'^([A-Z]+)_')

    # Keep only domestic rows (where Node == Source)
    domestic = supply_shares[supply_shares['Node'] == supply_shares['Source']].copy()

    # Merge with total supply to compute actual domestic amount
    df = domestic.merge(supply_df, on='Node')  # Now we have 'Share' and total 'Supply'

    # Calculate domestic supply = total supply × share
    df['Domestic_Supply'] = df['Supply'] * df['Share']

    # Add domestic emission factor from dfs_emission_factors_dom
    df = df.merge(dfs_emission_factors_dom, on='Node')  # Adds 'Factor'

    # Emissions = domestic supply × domestic factor
    df['Domestic_Emissions'] = df['Domestic_Supply'] * df['Factor']

    # Return result
    return df[['Node', 'Domestic_Emissions']].reset_index(drop=True)

def combine_total_emissions(import_emissions_df, domestic_emissions_df, only_EU=False, dfs_EU_countries=None):
    """
    Combines import and domestic emissions into a single DataFrame with totals,
    and removes rows with zero total emissions. Optionally filters to EU countries only.
    
    Parameters:
    - import_emissions_df: DataFrame with ['Node', 'Emissions']
    - domestic_emissions_df: DataFrame with ['Node', 'Domestic_Emissions']
    - only_EU: bool, if True filters to EU countries using dfs_EU_countries
    - dfs_EU_countries: optional DataFrame with 'EU' column and Node as index
    
    Returns:
    - DataFrame with ['Node', 'Import_Emissions', 'Domestic_Emissions', 'Total_Emissions']
      excluding rows where total emissions are zero and optionally non-EU countries.
    
    Raises:
    - ValueError if only_EU is True but dfs_EU_countries is not provided.
    """
    # Rename for clarity
    import_emissions = import_emissions_df.rename(columns={'Emissions': 'Import_Emissions'})
    domestic_emissions = domestic_emissions_df.rename(columns={'Domestic_Emissions': 'Domestic_Emissions'})

    # Merge both DataFrames on Node, fill missing with 0
    combined = pd.merge(import_emissions, domestic_emissions, on='Node', how='outer').fillna(0)

    # Add total emissions column
    combined['Total_Emissions'] = combined['Import_Emissions'] + combined['Domestic_Emissions']

    # Remove rows with zero total emissions
    combined = combined[combined['Total_Emissions'] > 0]

    # Optional filtering to EU countries
    if only_EU:
        if dfs_EU_countries is None:
            raise ValueError("dfs_EU_countries must be provided when only_EU is True.")
        eu_nodes = dfs_EU_countries[dfs_EU_countries['EU'] == True].index
        combined = combined[combined['Node'].isin(eu_nodes)]

    return combined.reset_index(drop=True)[['Node', 'Import_Emissions', 'Domestic_Emissions', 'Total_Emissions']]



def calculate_total_emissions(combined_emissions_df):
    """
    Calculates total import, domestic, and combined emissions from the combined DataFrame.
    
    Parameters:
    - combined_emissions_df: DataFrame with columns:
        - 'Import_Emissions'
        - 'Domestic_Emissions'
        - 'Total_Emissions'
    
    Returns:
    - Dictionary with total values for each emission type
    """
    totals = {
        'Total_Import_Emissions': combined_emissions_df['Import_Emissions'].sum(),
        'Total_Domestic_Emissions': combined_emissions_df['Domestic_Emissions'].sum(),
        'Total_Emissions': combined_emissions_df['Total_Emissions'].sum()
    }
    return totals

def build_emissions_summary(**kwargs):
    """
    Combines multiple emissions totals dicts into a single DataFrame.
    
    Parameters:
    - kwargs: named totals dictionaries, e.g., totals_2021=..., totals_2024=...
    
    Returns:
    - DataFrame with scenario names as rows and emissions metrics as columns
    """
    records = []
    for key, totals_dict in kwargs.items():
        # Extract label after 'totals_' for row name
        label = key.replace('totals_', '')
        row = {'Scenario': label}
        row.update(totals_dict)
        records.append(row)
    
    return pd.DataFrame(records).set_index('Scenario')



def calculate_average_emission_factor_from_totals(scenario, total_emissions_df, demand_df,
                                                  only_EU=False, dfs_EU_countries=None):
    """
    Calculates average upstream emission factor from total emissions and demand.
    Returns a tuple: (scenario, average_emission_factor)
    """

    emissions = total_emissions_df.copy()
    demand = demand_df.copy()

    if only_EU:
        if dfs_EU_countries is None:
            raise ValueError("dfs_EU_countries must be provided when only_EU is True.")
        eu_nodes = dfs_EU_countries[dfs_EU_countries['EU'] == True].index
        emissions = emissions[emissions['Node'].isin(eu_nodes)]
        demand = demand[demand['Node'].isin(eu_nodes)]

    # Keep only nodes that exist in both dfs
    df = demand.merge(emissions[['Node', 'Total_Emissions']], on='Node', how='inner')

    total_emissions = df['Total_Emissions'].sum()
    total_demand = df['Supply'].sum()

    avg_ef = total_emissions / total_demand if total_demand > 0 else 0

    return scenario, avg_ef


