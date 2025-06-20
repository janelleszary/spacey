# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Print basic statistics and structure of the DataFrame for debugging purposes
# spacex_df.head(5)
# spacex_df.describe()
# spacex_df.info()

# Create a dash application
app = dash.Dash(__name__)

# Dropdown options
options = [{'label': 'All Sites', 'value': 'ALL'}]
for ls in spacex_df["Launch Site"].unique():
    options.append({"label":ls, "value":ls})

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                    options=options,
                                    value="ALL",
                                    placeholder="select a launch site here",
                                    searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                # TASK 3: Add a slider to select payload range
                                html.P("Payload range (Kg):"),
                                dcc.RangeSlider(id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback( Output(component_id="success-pie-chart", component_property='figure'),
               Input(component_id='site-dropdown', component_property='value'))    
def get_pie_chart(selected_site):
    if selected_site=="ALL":
        data = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(data, values='class',names='Launch Site',title = "Successes by Site")
    else:
        data = spacex_df[spacex_df["Launch Site"]==selected_site]
        data = data.groupby(['class'])['Flight Number'].count().reset_index()
        data.rename(columns={"Flight Number": "Count"}, inplace=True)
        fig = px.pie(data, values='Count',names='class',title = "Successes at {}".format(selected_site))
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback( Output(component_id="success-payload-scatter-chart", component_property='figure'),
            [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")])
def get_scatter_chart(selected_site, slider_vals):
    if selected_site=="ALL":
        fig = px.scatter(spacex_df,
                        x='Payload Mass (kg)',
                        y='class',
                        color='Booster Version Category',
                        title="Correlation Between Payload and Class for ALL Sites")
    else:
        data = spacex_df[spacex_df["Launch Site"]==selected_site]
        fig = px.scatter(data,
                        x='Payload Mass (kg)',
                        y='class',
                        color='Booster Version Category',
                        title="Correlation Between Payload and Class for {}".format(selected_site))
    fig.update_xaxes(range=slider_vals)
    return fig


# Run the app
import os
if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), 
            port=int(os.getenv('PORT', 4444)))