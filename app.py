
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

subvolume = misc.stack_to_numpy(data_path)
vol_fig = misc.plotly_volume_rendering(subvolume)


###########

# TODO: other options: color scheme, min/max

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
#app= Dash(__name__)

app.layout = html.Div(children=[
    html.H2(
        children=f'{data_path}',
        style={
            'textAlign': 'center'
            }
    ),
    html.Div(children=[
        html.H4('x-slice', style={'textAlign': 'center'}),
        dcc.Graph(id='x-slice'),
        dcc.Slider(
            min=0,
            max=(np.shape(subvolume)[0])-1,
            step=1,
            marks={i: f'{i}' for i in range(np.shape(subvolume)[0]) if i%5==0},
            value=0,
            id='x-slice-slider'
            )
    ]),
    html.Div(children=[
        html.H4('y-slice', style={'textAlign': 'center'}),
        dcc.Graph(id='y-slice'),
        dcc.Slider(
            min=0,
            max=(np.shape(subvolume)[1])-1,
            step=1,
            marks={i: f'{i}' for i in range(np.shape(subvolume)[1]) if i%5==0},
            value=0,
            id='y-slice-slider'
            )
    ]),
    html.Div(children=[
        html.H4('z-slice', style={'textAlign': 'center'}),
        dcc.Graph(id='z-slice'),
        dcc.Slider(
            min=0,
            max=(np.shape(subvolume)[2])-1,
            step=1,
            marks={i: f'{i}' for i in range(np.shape(subvolume)[2]) if i%5==0},
            value=0,
            id='z-slice-slider'
            )
    ]),
    html.Div(
        dcc.Graph(figure=vol_fig)
    ),

#    html.Div(
#        dbc.Row([
#        dbc.Col(
#            dash.html.Div(dash.dcc.Graph(figure=fig_heatmap0)), width={'size':3}
#            ),
#        dbc.Col(
#            dash.html.Div(dash.dcc.Graph(figure=fig_heatmap1)), width={'size':3}
#            ),
#        dbc.Col(
#            dash.html.Div(dash.dcc.Graph(figure=fig_heatmap1)), width={'size':3}
#            )
#        ])
])

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
                    zmax=np.percentile(subvolume, 92))


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

