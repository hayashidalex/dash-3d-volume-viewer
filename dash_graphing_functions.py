import plotly.graph_objects as go 
import plotly.express as px
from plotly.subplots import make_subplots

import numpy as np
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
import io
import math


def render_plotly_volume_view(vol_array, 
                            output_bytes=False, 
                            axis = 'z',
                            name='3D volume', 
                            voxel_size_um = 1.0,
                            colorscale='rainbow',
                            min_pct = 2,
                            max_pct = 98,
                            opacity=0.3, opacityscale=0.3,
                            surface_count=12):
    '''
    Generates 3D plotly figure
    Args:
        vol_array(numpy 3D array):
        output_bytes(boolean): True for byte array, 
                               False for plotly.graph_object.Figure
        name(str):
        voxel_size_um(float):
        colorsacle(str):
        opacity(float):
        opacityscale(float):
        surface_count(int): should not be too large or too small
    Returns:
        plotly figure(plotly.graph_object.Figure) or its byte_array version
    '''

    # calculate min and max values
    minval = np.percentile(vol_array, min_pct)
    maxval = np.percentile(vol_array, max_pct)


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
          isomax = maxval,
          isomin = minval,
          slices_z = dict(show=True, locations=[10]),
        )
    fig_3d = go.Figure(data=vol)

    # Tick customization
    vals = []
    texts = []
    for i in range (0,max(vol_array.shape),8):
      vals.append(i)
      texts.append(str(i*voxel_size_um))


    if axis == 'x':                                                    
        up_direction = dict(x=1, y=0, z=0)                                  
        eye = dict(x=1.25, y=1.25, z=1.25)                                  
    elif axis == 'y':                                                  
        up_direction = dict(x=0, y=1, z=0)                                  
        eye = dict(x=1.25, y=1.25, z=1.25)                                  
    else: # axis == 'z'                                                
        up_direction = dict(x=0, y=0, z=1)                                  
        eye = dict(x=-1.25, y=1.25, z=1.25)  


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
                        scene_aspectmode='data',
                        scene_camera = dict(up=up_direction, eye=eye),
                        margin=dict(l=20, r=20, t=100, b=100, pad=4),
                        paper_bgcolor="LightBlue",
                        height=600)

    if output_bytes:
        plotly_bytes = fig_3d.to_image(format="png")
        return io.BytesIO(plotly_bytes)

    else:
        return fig_3d



def slices_along_axis(vol_array, axis, output_bytes=False,
                      min_pct=2, max_pct=98, colormap="rainbow", imgs_in_row=6, 
                      title=None):
    '''
    Args:
        vol_array(numpy 3D array):
        output_bytes(boolean): True for byte array, 
                               False for plotly.graph_object.Figure

    Returns:
        byte_array
        if outfile is given, image is also saved
    '''

    # Figure out row/column sizes
    size_x, size_y, size_z = np.shape(vol_array)
    
    if axis == 'x':
        img_count, img_width, img_height = size_x, size_y, size_z
    elif axis == 'y':
        img_count, img_width, img_height = size_y, size_z, size_x
    elif axis == 'z':
        img_count, img_width, img_height = size_z, size_y, size_x
    
    row_count = math.ceil(img_count/imgs_in_row)
    figsize = (imgs_in_row*img_width*3, row_count*img_height*3) 
    # divisor is just for a friendly size. May need to be smaller
    
    # calculate min and max values
    vmin = np.percentile(vol_array, min_pct)
    vmax = np.percentile(vol_array, max_pct)

    fig = make_subplots(rows=row_count, cols=imgs_in_row)
    
    for j in range(row_count):
        for i in range(imgs_in_row):
            if j*imgs_in_row+i < img_count:
                if axis == 'x':
                    fig.add_trace(go.Heatmap(z=vol_array[j*imgs_in_row+i, :, :],
                                  zmin=vmin, zmax=vmax,
                                  colorscale=colormap,
                                  ), row=j+1, col=i+1)

                elif axis == 'y':
                    fig.add_trace(go.Heatmap(z=vol_array[:, j*imgs_in_row+i, :],
                                  zmin=vmin, zmax=vmax,
                                  colorscale=colormap,
                                  ), row=j+1, col=i+1)
                else:
                    fig.add_trace(go.Heatmap(z=vol_array[:, :, j*imgs_in_row+i],
                                  zmin=vmin, zmax=vmax,
                                  colorscale=colormap,
                                  ), row=j+1, col=i+1)
                fig.update_xaxes(visible=False, showticklabels=False, row=j+1, col=i+1)
                fig.update_yaxes(visible=False, showticklabels=False, row=j+1, col=i+1)

    fig.update_layout(showlegend=False)
    
    if output_bytes:  
        slices_bytes = fig.to_image(format="png", width=figsize[0], height=figsize[1])
        return io.BytesIO(slices_bytes)

    else:
        return fig



def generate_2D_summary(vol_array, outfile=None, min_pct=2, max_pct=98, 
                        colormap="rainbow", imgs_in_row=4, title=None):

    '''
    Return:
        img_byte_arr: byte array
    '''

    images = []                                                             
    for axis in ['x', 'y', 'z']:
        slice_img = slices_along_axis(vol_array, axis, 
                                      output_bytes=True,
                                      min_pct=min_pct, 
                                      max_pct=max_pct,
                                      colormap=colormap,
                                      imgs_in_row=imgs_in_row,
                                      title=title)

        images.append(slice_img)   
        
    # Convert the byte arrays to viewable images and concatenate               
    graphs = [Image.open(img) for img in images]                               

    img_size = [0,0] # (width, height)  

    for graph in graphs:                                                  
        if graph.width > img_size[0]:                                          
            img_size[0] = graph.width                                          
        img_size[1] = img_size[1] + graph.height                               
                                                                           
    summary_img = Image.new('RGB', (img_size[0], img_size[1]))                 
    current_pos = [0,0]                                                        
                                                                        
    ##  Stitch all graphs together                                          
    # Matplotlib images                                                     
    for graph in graphs:                                               
        summary_img.paste(graph,  current_pos)                              
        # bring the current position down by the pasted image's height      
        current_pos = (0, current_pos[1] + graph.height) 

    if outfile:
        summary_img.save(outfile)

    for img in images:
        img.close()


    # Convert to byte array
    img_byte_arr = io.BytesIO()
    summary_img.save(img_byte_arr, format='PNG')
    
    return img_byte_arr



def generate_summary(vol_array, outfile=None, min_pct=92, max_pct=98, 
                     colormap_2D="rainbow", imgs_in_row=4, title_2D=None,
                     title_3D=None, voxel_size_um=1.0, colorscale_3D="rainbow",
                     opacity=0.3, opacityscale=0.3, surface_count=12):
    '''
    Generate a summary of 3D volume rendering. If outfile name is given
    (e.g., output.png), it saves as such; otherwise, returns a byte array.
    Args:
        vol_array(numpy 3D array):
        outfile(str): /path/to/output/file.png
    Returns:
        if outfile: None (data saved)
        else: byte array
    '''

    #QUESTION: Should min_pct and max_pct for 2D and 3D be separated? 
    #QUESTION: Should this be combined with the method above?

    images = []                                              

    # 2D images
    for axis in ['x', 'y', 'z']:
        slice_img = slices_along_axis(vol_array, axis, 
                                      output_bytes=True,
                                      min_pct=min_pct, 
                                      max_pct=max_pct,
                                      colormap=colormap_2D,
                                      imgs_in_row=imgs_in_row,
                                      title=title_2D)

        images.append(slice_img)   


    # Render 3D Images
    for axis in ['x','y','z']:
        plotly_img = render_plotly_volume_view(vol_array, 
                                               output_bytes=True, 
                                               axis=axis,
                                               name=title_3D,
                                               voxel_size_um=voxel_size_um,
                                               colorscale=colorscale_3D,
                                               min_pct=min_pct,
                                               max_pct=max_pct,
                                               opacity=opacity,
                                               opacityscale=opacityscale,
                                               surface_count=surface_count)
        images.append(plotly_img)


    # Convert the byte arrays to viewable images and concatenate
    graphs = [Image.open(img) for img in images]

    # At this point, there should be 6 images

    img_size = [0,0] # (width, height)

    for graph in graphs:
        if graph.width > img_size[0]:
            img_size[0] = graph.width
        img_size[1] = img_size[1] + graph.height

    summary_img = Image.new('RGB', (img_size[0], img_size[1]))
    current_pos=[0,0]

    ##  Stitch all graphs together
    for graph in graphs:
        summary_img.paste(graph,  current_pos)
        # bring the current position down by the pasted image's height
        current_pos = (0, current_pos[1] + graph.height)

    
    if outfile:
        summary_img.save(outfile)

    for img in images:
        img.close()

    # Convert to byte array
    img_byte_arr = io.BytesIO()
    summary_img.save(img_byte_arr, format='PNG')
    
    return img_byte_arr



def generate_plotly_video():
    '''
    create rotation video
    '''
