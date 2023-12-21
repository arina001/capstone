
'''
python -m pip install pandas dash
wget "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
wget "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/labs/module_3/spacex_dash_app.py"
python spacex_dash_app.py
'''
# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("data_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
print(spacex_df.tail(5))
#---------------------------------------------------------------------------------
# Create the dropdown menu options
#Dropdown helper

launch_sites_df = spacex_df[['Launch Site']].groupby(['Launch Site'], as_index=False).first()
launch_sites_list=list(launch_sites_df['Launch Site'])
launch_sites_list.append('ALL SITES')


#---------------------------------------------------------------------------------

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                    style={'textAlign': 'center', 'color': '#503D36',
                    'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[{'label': i, 'value': i} for i in launch_sites_list],
                                    placeholder="Select a Launch Site here",
                                    value=str(launch_sites_list[-1]),
                                    searchable=True,
                                    ),

                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',min=0,max=10000,step=1000,value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),

                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input - launch site  and output - pie graph
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
            Input(component_id='site-dropdown', component_property='value'))

# return the outcomes piechart for a selected site
def get_pie_chart(entered_site):

    if entered_site =='ALL SITES':
        filtered_df=spacex_df
        fig = px.pie(data_frame=filtered_df,
            values='class',
            names= 'Launch Site')
        fig.update_layout(title_text='Total Launches by Site Name(Florida: KSC,CCAFS; CALIFORNIA: VAFB)', title_x=0.5, )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        filtered_df = filtered_df.groupby(['class']).count().reset_index()
        filtered_df['class']=['Fail','Succes']
        data = filtered_df[['class','Flight Number']]
        fig = px.pie(data,
            values='Flight Number',
            names= 'class')
        fig.update_layout(title_text='Succes Failure Launch Site {}'.format(entered_site), title_x=0.5)
    return fig



# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value')])

def success_payload_scatter_chart(selected_site,slider_range):
    low, high = slider_range
    if selected_site=='ALL SITES':
        filtered_df=spacex_df
        # apply slider filter - payload within range
        filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= low) & (filtered_df['Payload Mass (kg)'] <= high)]
        # search for success only
        #filtered_df = filtered_df[filtered_df['class']==1].reset_index()
        #print(filtered_df.head())

        scatter=px.scatter(
            data_frame=filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            color_continuous_scale='Plotly3')
        scatter.update_layout(title_text='Correlation between Payload and Success for All Sites',
                            title_x=0.5,
                            plot_bgcolor='wheat')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= low) & (filtered_df['Payload Mass (kg)'] <= high)]
        scatter=px.scatter(
            data_frame=filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            color_continuous_scale='Plotly3')
        scatter.update_layout(title_text='Correlation between Payload and Success for Launch Site {}'.format(selected_site),
                            title_x=0.5,
                            plot_bgcolor='beige')
    return scatter

# Run the app
if __name__ == '__main__':
    app.run_server()