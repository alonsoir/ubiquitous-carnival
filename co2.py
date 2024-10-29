import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from dash import Dash, dcc, html, Input, Output

# Load the datasets
emissions_per_capita = pd.read_csv('co-emissions-per-capita.csv')
emissions_by_region = pd.read_csv('annual-co-emissions-by-region.csv')

# Filter the datasets for the years 1970-2020
emissions_per_capita = emissions_per_capita[
    (emissions_per_capita['Year'] >= 1970) & (emissions_per_capita['Year'] <= 2020)]
emissions_by_region = emissions_by_region[(emissions_by_region['Year'] >= 1970) & (emissions_by_region['Year'] <= 2020)]

# Ensure only countries with a 3-letter ISO code are used
emissions_per_capita = emissions_per_capita[emissions_per_capita['Code'].str.len() == 3]
emissions_by_region = emissions_by_region[emissions_by_region['Code'].str.len() == 3]

# Aggregate total emissions from 1970 to 2020 to identify the top 10 countries
total_emissions = emissions_by_region.groupby('Entity').sum().sort_values(by='Annual CO₂ emissions',
                                                                          ascending=False).head(10)
top_10_countries = total_emissions.index.tolist()

# Filter the datasets to include only the top 10 countries
emissions_per_capita_top_10 = emissions_per_capita[emissions_per_capita['Entity'].isin(top_10_countries)]
emissions_by_region_top_10 = emissions_by_region[emissions_by_region['Entity'].isin(top_10_countries)]

# Initialize the Dash app (Note: the execution of this dashboard setup is not performed here)
app = Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id='year-selector',
        options=[{'label': year, 'value': year} for year in range(1970, 2021)],
        value=1970,
        clearable=False
    ),
    dcc.Graph(id='choropleth-map'),
    html.Div([
        dcc.Graph(id='stacked-area-chart'),
        dcc.Graph(id='line-chart-per-capita')
    ], style={'display': 'flex'})
])


@app.callback(
    Output('choropleth-map', 'figure'),
    Input('year-selector', 'value')
)
def update_map(selected_year):
    df_filtered_year = emissions_per_capita[emissions_per_capita['Year'] == selected_year]
    fig = px.choropleth(df_filtered_year, locations="Code",
                        color="Annual CO₂ emissions (per capita)",
                        hover_name="Entity",
                        color_continuous_scale="YlOrRd",
                        title=f"CO₂ Emissions Per Capita in {selected_year}")
    return fig


@app.callback(
    Output('stacked-area-chart', 'figure'),
    Output('line-chart-per-capita', 'figure'),
    Input('year-selector', 'value')
)
def update_charts(selected_year):
    # Stacked Area Chart for total emissions
    fig_area = px.area(emissions_by_region_top_10, x="Year", y="Annual CO₂ emissions",
                       color="Entity", title="Total CO₂ Emissions of Top 10 Countries (1970-2020)")

    # Line Chart for per-capita emissions
    fig_line = px.line(emissions_per_capita_top_10, x="Year", y="Annual CO₂ emissions (per capita)",
                       color="Entity", title="Per-Capita CO₂ Emissions of Top 10 Countries (1970-2020)")

    return fig_area, fig_line

app.run_server(debug=True)
# Note: To run the app, you would normally call app.run_server(debug=True)
# but this execution step is not performed here.
