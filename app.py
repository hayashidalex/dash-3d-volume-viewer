
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
                md=7
        ),
        dbc.Col(controls_2d, md=5),
        ]),
        html.Br(),
        html.Br(),
        dbc.Row(
            dcc.Graph(figure=vol_fig),
        )
    ]
)




##################################################
####### Callback functions for 2D slices #########
##################################################


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



if __name__ == '__main__':
    app.run_server(debug=True)

