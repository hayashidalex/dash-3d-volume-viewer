
# visit http://127.0.0.1:8050/ in your web browser.

import dash

import plotly.express as px
import plotly.graph_objects as go 
import plotly.express as px
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc

import numpy as np
from pathlib import Path
from PIL import Image
import re


##### Convert subvol stack TIF to numpy

# TODO: this should be reading an input

dataset = Path('data/36_54_54/')
files = list(dataset.glob('*.tif'))
files.sort(key=lambda f: int(re.sub(r'[^0-9]*', "", str(f))))
print(files)

subvolume = []
for f in files:
  i = Image.open(f)
  subvolume.append(np.array(Image.open(f), dtype=np.float32))

# convert to numpy
subvolume = np.array(subvolume)
print("numpy array shape: ", np.shape(subvolume))


###### 3D Plotly Figure #######
sv = subvolume
voxel_size_um = 12.0
X, Y, Z = np.mgrid[0:sv.shape[0], 0:sv.shape[1], 0:sv.shape[2]]
#X, Y, Z = np.mgrid[0:sv.shape[0]*voxel_size_um: sv.shape[0], 0:sv.shape[1]*voxel_size_um: sv.shape[1], 0:sv.shape[2]*voxel_size_um: sv.shape[2]]
vol = go.Volume(
      name="sample volume",
      x = X.flatten(),
      y = Y.flatten(),
      z = Z.flatten(),
      value = sv.flatten(),
      opacity = 0.3,
      opacityscale = 0.3,
      surface_count = 15,
      colorscale='rainbow',
      slices_z = dict(show=True, locations=[10]),
    )
fig_3d = go.Figure(data=vol)

# Tick customization
vals = []
texts = []
for i in range (0,54,8):
  vals.append(i)
  texts.append(str(i*voxel_size_um))

fig_3d.update_layout(scene = dict(
                    xaxis = dict(
                        ticktext=texts,
                        tickvals=vals),
                    yaxis = dict(
                        ticktext=texts,
                        tickvals=vals),
                    zaxis = dict(
                        ticktext=texts,
                        tickvals=vals)),
                        margin=dict(l=20, r=20, t=100, b=100, pad=4),
                        paper_bgcolor="LightBlue",
                        height=600)


# TODO: There should be a slider for slices

####### Heatmap Set-up ######
fig_heatmap0 = px.imshow(subvolume[0,:,:])
fig_heatmap1 = px.imshow(subvolume[:,0,:])
fig_heatmap2 = px.imshow(subvolume[:,:,0])


app= dash.Dash(__name__)

app.layout = dash.html.Div(children=[
    dash.html.H2(
        children=f'{dataset}',
        style={
            'textAlign': 'center'
            }
    ),
    dash.html.Div(
        dash.dcc.Graph(figure=fig_heatmap0)
    ),
    dash.html.Div(
        dash.dcc.Graph(figure=fig_heatmap1)
    ),
    dash.html.Div(
        dash.dcc.Graph(figure=fig_heatmap2)
    ),
    dash.html.Div(
        dash.dcc.Graph(figure=fig_3d)
    ),

#    dash.html.Div(
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


if __name__ == '__main__':
    app.run_server(debug=True)

