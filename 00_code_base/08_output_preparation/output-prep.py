# import packages
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots


output_file = r"C:\Users\mar.eco\OneDrive - CBS - Copenhagen Business School\Desktop\hydrogen_grid\01_data\02_output_data\02_unidirectional_results\01_paper_IAEE\01_raw_results\raw_investments_2021.csv"
input_file = r"C:\Users\mar.eco\OneDrive - CBS - Copenhagen Business School\Desktop\hydrogen_grid\01_data\01_input_data\02_processed\01_paper_IAEE\inputs_IAEE_2025_run_2024.xlsx"

df_output = pd.read_csv(output_file)
df_params = pd.read_excel(input_file, sheet_name="Parameters")

#print(df_output.columns)
#print(df_params.head())

output_2021 = r"C:\Users\mar.eco\OneDrive - CBS - Copenhagen Business School\Desktop\hydrogen_grid\01_data\02_output_data\02_unidirectional_results\01_paper_IAEE\02_prepared_results\output_2021_prepared.xlsx"
output_2024 = r"C:\Users\mar.eco\OneDrive - CBS - Copenhagen Business School\Desktop\hydrogen_grid\01_data\02_output_data\02_unidirectional_results\01_paper_IAEE\02_prepared_results\output_2024_prepared.xlsx"
df_output_2021 = pd.read_excel(output_2021,sheet_name='LNG_Sources')
df_output_2024 = pd.read_excel(output_2024, sheet_name='LNG_Sources')

print(df_output_2021.columns)
print(df_output_2024.columns)

country_map = {
    'AF': 'Afghanistan',
    'EG': 'Egypt',
    'QA': 'Qatar',
    'TT': 'Trinidad & Tobago',
    'USA': 'United States'
}

# Create a pie chart of sources for LNG
def plot_pie_charts(df1, column1, year1, df2, column2, year2):
    grouped1 = df1.groupby('Region')[column1].sum().sort_values(ascending=False)
    grouped1.index = grouped1.index.map(lambda x: country_map.get(x, x))
    grouped2 = df2.groupby('Region')[column2].sum().sort_values(ascending=False)
    grouped2.index = grouped2.index.map(lambda x: country_map.get(x, x))   

    fig, axs = plt.subplots(1, 2, figsize=(14, 7))

    axs[0].pie(grouped1, labels=grouped1.index, autopct='%1.1f%%', startangle=90)
    axs[0].set_title(f"🇪🇺 European LNG Sources ({year1})")

    axs[1].pie(grouped2, labels=grouped2.index, autopct='%1.1f%%', startangle=90)
    axs[1].set_title(f"🇪🇺 European LNG Sources ({year2})")

    plt.tight_layout()
    plt.show()

plot_pie_charts(df_output_2021, 'Flow (GWh).1', 2021, df_output_2024, 'Flow (GWh).1', 2024)



# Try and plot with plotly to see difference
def create_pie_chart(df1, df2, flow_column, year1, year2):
    df1['Country'] = df1['Region'].map(country_map).fillna(df1['Region'])
    df2['Country'] = df2['Region'].map(country_map).fillna(df2['Region'])

    # Group and sum flows
    grouped1 = df1.groupby('Country')[flow_column].sum()
    grouped2 = df2.groupby('Country')[flow_column].sum()

    # Create side-by-side pie charts
    fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]],
                        subplot_titles=[str(year1), str(year2)])

    fig.add_trace(go.Pie(labels=grouped1.index, values=grouped1.values, name=str(year1)),
                  row=1, col=1)
    fig.add_trace(go.Pie(labels=grouped2.index, values=grouped2.values, name=str(year2)),
                  row=1, col=2)

    fig.update_layout(
        title_text=f"European LNG import sources: {year1} vs {year2}",
        annotations=[
            dict(text=str(year1), x=0.18, y=0.5, font_size=14, showarrow=False),
            dict(text=str(year2), x=0.82, y=0.5, font_size=14, showarrow=False)
        ]
    )
    fig.show()


create_pie_chart(df_output_2021, df_output_2024, 'Flow (GWh).1', 2021, 2024)