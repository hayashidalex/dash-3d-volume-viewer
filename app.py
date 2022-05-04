
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, dcc, html, Input, Output

import plotly.express as px
import plotly.graph_objects as go 
import plotly.express as px
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc

import numpy as np

import miscellaneous_functions as misc


data_path='data/36_54_54/'


##########

subvolume = misc.stack_to_numpy(data_path)
vol_fig = misc.plotly_volume_rendering(subvolume)


###########


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# TODO: Make these actually work
controls = dbc.Card(
    [
        html.Div(
            [
                dbc.Label("X variable"),
                dcc.Dropdown(
                    id="color scheme",
                    options=['rainbow', 'viridis'],
                    value='rainbow',
                ),
            ]
        ),
        html.Div(
            [
                dbc.Label("max percentage"),
                dbc.Input(id="max-percent", type="number", value=92),
                
            ]
        ),
        html.Div(
            [
                dbc.Label("min percentage"),
                dbc.Input(id="min-percent", type="number", value=8),
            ]
        ),
    ],
    body=True,
)


app.layout = dbc.Container(
    [
        html.H2(f'{data_path}'),
        html.Hr(),
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
                md=6
        ),
        dbc.Col(
            [
                controls, 
                html.Br(),
                html.Br(),
                dcc.Graph(figure=vol_fig),
            ],
            md=6),
        ]
        ),
    ]
)




##################################################
####### Callback functions for 2D slices #########
##################################################


@app.callback(
    Output(component_id='x-slice', component_property='figure'),
    Input(component_id='x-slice-slider', component_property='value')
)
def update_x_slice(input_value):
    return px.imshow(subvolume[input_value,:,:], 
                    zmin=np.percentile(subvolume, 8), 
                    zmax=np.percentile(subvolume, 92),
                    color_continuous_scale='viridis')


@app.callback(
    Output(component_id='y-slice', component_property='figure'),
    Input(component_id='y-slice-slider', component_property='value')
)
def update_y_slice(input_value):
    return px.imshow(subvolume[:,input_value,:], 
                    zmin=np.percentile(subvolume, 8), 
                    zmax=np.percentile(subvolume, 92))


@app.callback(
    Output(component_id='z-slice', component_property='figure'),
    Input(component_id='z-slice-slider', component_property='value')
)
def update_x_slice(input_value):
    return px.imshow(subvolume[:,:,input_value], 
                    zmin=np.percentile(subvolume, 8), 
                    zmax=np.percentile(subvolume, 92))



if __name__ == '__main__':
    app.run_server(debug=True)

