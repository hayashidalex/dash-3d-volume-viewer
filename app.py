
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State

import plotly.express as px
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc

import numpy as np
import json
from json import JSONEncoder
from pathlib import Path

import miscellaneous_functions as misc


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


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
    style={'margin': 10} 
)

################
controls_3d = dbc.Card(
    [
        html.Div(
            [
                dbc.Label("Colormap"),
                dcc.Dropdown(
                    id="colormap_3d",
                    options=['rainbow', 'viridis', 'gray'],
                    value='rainbow',
                ),
            ]
        ),
        html.Div(
            [
                dbc.Label("Max percentage"),
                dbc.Input(id="max_percent_3d", type="number", value=92, min=1, max=100),
                
            ]
        ),
        html.Div(
            [
                dbc.Label("Min percentage"),
                dbc.Input(id="min_percent_3d", type="number", value=8, min=1, max=100),
            ]
        ),
        html.Div(
             dbc.Button(id='3d-request', style={'margin': 10}, n_clicks=0, children='3D Volume rendering')
        )
        
    ],
    body=True,
    style={'margin': 10}
)

download_buttons = dbc.Card(
    [
        dbc.Button(id='download-all', style={'margin': 10}, n_clicks=0, children='Download All'),
        dbc.Button(id='download-2d', style={'margin': 10}, n_clicks=0, children='Download 2D'),
    ],
    body=True,
)

########################

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

app.layout = dbc.Container(
    [
        html.H1(f'3D Volume Visualizer', style={'margin': 10}),
        html.Hr(),
        html.Br(),
        html.Div(
            [
                dbc.Label("Input Dataset"),
                dbc.Input(id="dataset", type="text", required=True, 
                    placeholder="path/to/dir/containing/tif/files"),
                dbc.Button(id='submit-button-state', style={'margin': 10}, n_clicks=0, children='Submit'),
                html.Div(id='dataset-selection')
            ], 
        ),
        dcc.Store(id='intermediate-value'),
        html.Br(),
        html.Br(),
        dbc.Row(
        [
        dbc.Col(
            
                dbc.Row(
                    [
                    dcc.Graph(id='x-slice'),
                    html.Div(id='x_slider_display'),
                    html.Hr(),
                    dcc.Graph(id='y-slice'),
                    html.Div(id='y_slider_display'),
                    html.Hr(),
                    dcc.Graph(id='z-slice'),
                    html.Div(id='z_slider_display'),
                    html.Hr(),
                    ],
                    align="center",
                ),
                md=7
        ),
        dbc.Col([
            dbc.Row(controls_2d), 
            dbc.Row(download_buttons)
            ],
            md=5
        ),
        ]),
        html.Br(),
        html.Br(),
        #html.Div(
        #    [
        #        dbc.Button(id='3d-request', style={'margin': 10}, n_clicks=0, children='3D Volume rendering'),
        #    ]
        #),
        dbc.Row([
            dbc.Col(
                dcc.Graph(id='plotly_vol'),
                md=7
            ),
            dbc.Col(controls_3d, md=5),
        ])
    ]
)

### Callbacks for Dataset selection

@app.callback(
    Output(component_id='intermediate-value', component_property='data'),
    Input('submit-button-state', 'n_clicks'),
    State(component_id='dataset', component_property='value'),
    prevent_initial_call=True
    )
def get_array(n_clicks, data_path):
    if n_clicks is None:
        raise PreventUpdate
    else:

        if Path(data_path).suffix == ".npy":
            volume = misc.numpy_binary_to_array(data_path)

        elif Path(data_path).is_dir:
            volume = misc.stack_to_numpy(data_path)
        
        else:
            print("Incorrect input")
            volume = np.zeros((1,1,1))
        
        encodedNumpyData = json.dumps({"volume": volume}, cls=NumpyArrayEncoder)
        return encodedNumpyData


## Print the size of the selected volume array
@app.callback(
    Output(component_id='dataset-selection', component_property='children'),
    Input(component_id='intermediate-value', component_property='data'),    
    prevent_initial_call=True
)
def print_volume_size(jsonified_volume):
    decodedArray = json.loads(jsonified_volume)
    data_array = np.asarray(decodedArray["volume"])
    
    return f"volume shape: {np.shape(data_array)}"



### Callbacks for 2D sliders

@app.callback(
    Output(component_id='x_slider_display', component_property='children'),
    Input(component_id='intermediate-value', component_property='data'),    
    prevent_initial_call=True
)
def set_x_slider(jsonified_volume):
    
    decodedArray = json.loads(jsonified_volume)
    data_array = np.asarray(decodedArray["volume"])

    return dcc.Slider(
           min=0,
           max=(np.shape(data_array)[0])-1,
           step=1,
           marks={i: f'{i}' for i in range(np.shape(data_array)[0]) if i%5==0},
           value=0,
           id='x_slider'
           )

@app.callback(
    Output(component_id='y_slider_display', component_property='children'),
    Input(component_id='intermediate-value', component_property='data'),    
    prevent_initial_call=True
)
def set_y_slider(jsonified_volume):
    
    decodedArray = json.loads(jsonified_volume)
    data_array = np.asarray(decodedArray["volume"])

    return dcc.Slider(
           min=0,
           max=(np.shape(data_array)[1])-1,
           step=1,
           marks={i: f'{i}' for i in range(np.shape(data_array)[1]) if i%5==0},
           value=0,
           id='y_slider'
           )

@app.callback(
    Output(component_id='z_slider_display', component_property='children'),
    Input(component_id='intermediate-value', component_property='data'),    
    prevent_initial_call=True
)
def set_z_slider(jsonified_volume):
    
    decodedArray = json.loads(jsonified_volume)
    data_array = np.asarray(decodedArray["volume"])

    return dcc.Slider(
           min=0,
           max=(np.shape(data_array)[2])-1,
           step=1,
           marks={i: f'{i}' for i in range(np.shape(data_array)[2]) if i%5==0},
           value=0,
           id='z_slider'
           )


#### Callbacks for 2D slices


@app.callback(
    Output(component_id='x-slice', component_property='figure'),
    Input(component_id='intermediate-value', component_property='data'),
    Input(component_id='x_slider', component_property='value'),
    Input(component_id='colormap', component_property='value'),
    Input(component_id='max_percent', component_property='value'),
    Input(component_id='min_percent', component_property='value'),
    prevent_initial_call=True, 
    
)
def update_x_slice(jsonified_volume, slice_n, colormap, max_percent, min_percent):
    decodedArray = json.loads(jsonified_volume)
    data_array = np.asarray(decodedArray["volume"])

    return px.imshow(data_array[slice_n,:,:], 
                    zmin=np.percentile(data_array, min_percent), 
                    zmax=np.percentile(data_array, max_percent),
                    color_continuous_scale=colormap)

@app.callback(
    Output(component_id='y-slice', component_property='figure'),
    Input(component_id='intermediate-value', component_property='data'),
    Input(component_id='y_slider', component_property='value'),
    Input(component_id='colormap', component_property='value'),
    Input(component_id='max_percent', component_property='value'),
    Input(component_id='min_percent', component_property='value'),
    prevent_initial_call=True, 
)
def update_y_slice(jsonified_volume, slice_n, colormap, max_percent, min_percent):
    decodedArray = json.loads(jsonified_volume)
    data_array = np.asarray(decodedArray["volume"])

    return px.imshow(data_array[:,slice_n,:], 
                    zmin=np.percentile(data_array, min_percent), 
                    zmax=np.percentile(data_array, max_percent),
                    color_continuous_scale=colormap)


@app.callback(
    Output(component_id='z-slice', component_property='figure'),
    Input(component_id='intermediate-value', component_property='data'),
    Input(component_id='z_slider', component_property='value'),
    Input(component_id='colormap', component_property='value'),
    Input(component_id='max_percent', component_property='value'),
    Input(component_id='min_percent', component_property='value'),
    prevent_initial_call=True, 
)
def update_z_slice(jsonified_volume, slice_n, colormap, max_percent, min_percent):
    decodedArray = json.loads(jsonified_volume)
    data_array = np.asarray(decodedArray["volume"])

    return px.imshow(data_array[:,:,slice_n], 
                    zmin=np.percentile(data_array, min_percent), 
                    zmax=np.percentile(data_array, max_percent),
                    color_continuous_scale=colormap)


### Callback for 3D Plotly volume rendering

@app.callback(
    Output(component_id='plotly_vol', component_property='figure'),
    Input(component_id='3d-request', component_property='n_clicks'),
    State(component_id='intermediate-value', component_property='data'),
    prevent_initial_call=True
)
def update_plotly_3D(n_clicks, jsonified_volume):
    if n_clicks is None:
        raise PreventUpdate
    else:
        decodedArray = json.loads(jsonified_volume)
        data_array = np.asarray(decodedArray["volume"])

        return misc.plotly_volume_rendering(data_array) 


########### End of Callbacks #############


if __name__ == '__main__':
    app.run_server(debug=True)

