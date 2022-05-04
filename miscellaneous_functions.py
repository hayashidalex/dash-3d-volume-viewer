import plotly.graph_objects as go 
import plotly.express as px
import numpy as np
from pathlib import Path
from PIL import Image
import re


def stack_to_numpy(stack_path):
    '''
    Convert subvol stack TIF to numpy
    Args:
        stack_path(str): path/to/directory/containing/numbered/tif/files
    Returns:
        numpy 3D array
    '''

    dataset = Path(stack_path)
    files = list(dataset.glob('*.tif'))
    files.sort(key=lambda f: int(re.sub(r'[^0-9]*', "", str(f))))
    
    subvolume = []
    for f in files:
      subvolume.append(np.array(Image.open(f), dtype=np.float32))
    
    # convert to numpy
    subvolume = np.array(subvolume)
    print("numpy array shape: ", np.shape(subvolume))

    return subvolume


def plotly_volume_rendering(vol_array, name='3D volume', voxel_size_um = 1.0,
                            colorscale='rainbow', 
                            opacity=0.3, opacityscale=0.3,
                            surface_count=15):
    '''
    Generates 3D plotly figure
    Args:
        vol_array(numpy 3D array): 
        name(str):
        voxel_size_um(float):
        colorsacle(str):
        opacity(float):
        opacityscale(float):
        surface_count(int): should not be too large or too small
    Returns:
        plotly figure
    '''

    ###### 3D Plotly Figure #######
 
    X, Y, Z = np.mgrid[0:vol_array.shape[0], 0:vol_array.shape[1], 0:vol_array.shape[2]]
    vol = go.Volume(
          name=name,
          x = X.flatten(),
          y = Y.flatten(),
          z = Z.flatten(),
          value = vol_array.flatten(),
          opacity = opacity,
          opacityscale = opacityscale,
          surface_count = surface_count,
          colorscale=colorscale,
          slices_z = dict(show=True, locations=[10]),
        )
    fig_3d = go.Figure(data=vol)
    
    # Tick customization
    vals = []
    texts = []
    for i in range (0,max(vol_array.shape),8):
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
    
    return fig_3d

