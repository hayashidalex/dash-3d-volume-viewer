
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State

import plotly.express as px
import plotly.graph_objects as go 
import plotly.express as px
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc

import numpy as np

import miscellaneous_functions as misc


#############
# To make data_path as a callback, 
# see app_test.py for getting to numpy
# Then that has to be saved as dcc.Store
# See https://dash.plotly.com/sharing-data-between-callbacks
##############



data_path='data/36_54_54/'
subvolume = misc.stack_to_numpy(data_path)
vol_fig = misc.plotly_volume_rendering(subvolume)


#############################################


controls_2d = dbc.Card(
    [
        html.Div(
            [
                dbc.Label("Colormap"),
                dcc.Dropdown(
                    id="colormap",
                    options=['rainbow', 'viridis', 'gray'],
                    value='rainbow',
                ),
            ]
        ),
        html.Div(
            [
                dbc.Label("Max percentage"),
                dbc.Input(id="max_percent", type="number", value=92, min=1, max=100),
                
            ]
        ),
        html.Div(
            [
                dbc.Label("Min percentage"),
                dbc.Input(id="min_percent", type="number", value=8, min=1, max=100),
            ]
        ),
    ],
    body=True,
)



app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        html.H1(f'3D Volume Visualizer'),
        html.Hr(),
        html.Br(),
        html.Div(
            [
                dbc.Label("Input Dataset"),
                dbc.Input(id="dataset", type="text", required=True, 
                    placeholder="path/to/dir/containing/tif/files"),
                html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
                html.Div(id='dataset-selection')
            ]
        ),
        html.Br(),
        html.Br(),
        dbc.Row(
        [
        dbc.Col(
            
                dbc.Row(
                    [
                    dcc.Graph(id='x-slice'),
                    dcc.Slider(
                        min=0,
                        max=(np.shape(subvolume)[0])-1,
                        step=1,
                        marks={i: f'{i}' for i in range(np.shape(subvolume)[0]) if i%5==0},
                        value=0,
                        id='x-slice-slider'
                        ),
                    html.Hr(),
                    dcc.Graph(id='y-slice'),
                    dcc.Slider(
                        min=0,
                        max=(np.shape(subvolume)[1])-1,
                        step=1,
                        marks={i: f'{i}' for i in range(np.shape(subvolume)[1]) if i%5==0},
                        value=0,
                        id='y-slice-slider'
                        ),
                    html.Hr(),
                    dcc.Graph(id='z-slice'),
                    dcc.Slider(
                        min=0,
                        max=(np.shape(subvolume)[2])-1,
                        step=1,
                        marks={i: f'{i}' for i in range(np.shape(subvolume)[2]) if i%5==0},
                        value=0,
                        id='z-slice-slider'
                        ),
                     html.Hr(),
                    ],
                    align="center",
                ),
                md=7
        ),
        dbc.Col(controls_2d, md=5),
        ]),
        html.Br(),
        html.Br(),
        dbc.Row(
            dcc.Graph(id='plotly_vol'),
        )
    ]
)

################## 
### Callback for Dataset selection
##################

@app.callback(
    Output(component_id='dataset-selection', component_property='children'),
    Input('submit-button-state', 'n_clicks'),
    State(component_id='dataset', component_property='value'),
    prevent_initial_call=True
    )
def get_array(n_clicks, data_path):
    if n_clicks is None:
        raise PreventUpdate
    else:
        subvolume = misc.stack_to_numpy(data_path)
        return f'subvolume: {np.shape(subvolume)}'


##### 2D sliders
#
#@app.callback(
#    Output(component_id='x_slider', component_property='children'),
#    Input(component_id='data_array', component_property='value'),
#)
#def set_x_slider(data_array):
#    return dcc.Slider(
#           min=0,
#           max=(np.shape(data_array)[0])-1,
#           step=1,
#           marks={i: f'{i}' for i in range(np.shape(data_array)[0]) if i%5==0},
#           value=0,
#           )
#
#

####### Callback functions for 2D slices #########


@app.callback(
    Output(component_id='x-slice', component_property='figure'),
    Input(component_id='x-slice-slider', component_property='value'),
    Input(component_id='colormap', component_property='value'),
    Input(component_id='max_percent', component_property='value'),
    Input(component_id='min_percent', component_property='value'),
)
def update_x_slice(input_value, colormap, max_percent, min_percent):
    return px.imshow(subvolume[input_value,:,:], 
                    zmin=np.percentile(subvolume, min_percent), 
                    zmax=np.percentile(subvolume, max_percent),
                    color_continuous_scale=colormap)



@app.callback(
    Output(component_id='y-slice', component_property='figure'),
    Input(component_id='y-slice-slider', component_property='value'),
    Input(component_id='colormap', component_property='value'),
    Input(component_id='max_percent', component_property='value'),
    Input(component_id='min_percent', component_property='value'),
)
def update_y_slice(input_value, colormap, max_percent, min_percent):
    return px.imshow(subvolume[:,input_value,:], 
                    zmin=np.percentile(subvolume, min_percent), 
                    zmax=np.percentile(subvolume, max_percent),
                    color_continuous_scale=colormap)



@app.callback(
    Output(component_id='z-slice', component_property='figure'),
    Input(component_id='z-slice-slider', component_property='value'),
    Input(component_id='colormap', component_property='value'),
    Input(component_id='max_percent', component_property='value'),
    Input(component_id='min_percent', component_property='value'),
)
def update_z_slice(input_value, colormap, max_percent, min_percent):
    return px.imshow(subvolume[:,:,input_value], 
                    zmin=np.percentile(subvolume, min_percent), 
                    zmax=np.percentile(subvolume, max_percent),
                    color_continuous_scale=colormap)


##############
#@app.callback(
#    Output(component_id='plotly_vol', component_property='figure'),
#    Input(component_id='data_array', component_property='value') 
#)
#def update_plotly_3D(subvolume):
#    return misc.plotly_volume_rendering(subvolume) 
#


if __name__ == '__main__':
    app.run_server(debug=True)

