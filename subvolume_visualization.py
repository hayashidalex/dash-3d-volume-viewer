import math
import io
import argparse
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from PIL import Image
import numpy as np

import miscellaneous_functions as misc


## TODO:
# - docstring
# - color options
# - 3D min/max should be percentage 


def get_data_array(input_dir):
    
    return misc.stack_to_array(input_dir)


def render_slices(subvol, direction, cmap_choice="jet", imgs_in_row=6, 
                  save_img=True):

    size_x, size_y, size_z = np.shape(subvol)

    if direction == 'x':
        img_count, img_width, img_height = size_x, size_y, size_z
    elif direction == 'y':
        img_count, img_width, img_height = size_y, size_z, size_x
    elif direction == 'z':
        img_count, img_width, img_height = size_z, size_y, size_x

    print("img_count: ", img_count)
    row_count = math.ceil(img_count/imgs_in_row)

    print("row_count: ", row_count)
    figsize = (imgs_in_row*img_width/15, row_count*img_height/12) 
    # divisor is just for a friendly size. May need to be smaller

    # set up the graph
    f, ax_arr = plt.subplots(row_count, imgs_in_row, figsize=figsize)

    for j, row in enumerate(ax_arr):
        for i, ax in enumerate(row):
            if j*imgs_in_row+i < img_count:
                if direction == 'x':
                    ax.imshow(subvol[j*imgs_in_row+i, :, :],cmap=cmap_choice)
                    ax.set_title(f'x-slice {j*imgs_in_row+i}')
                elif direction == 'y':
                    ax.imshow(subvol[:,j*imgs_in_row+i, :],cmap=cmap_choice)
                    ax.set_title(f'y-slice {j*imgs_in_row+i}')
                else:  # z
                    ax.imshow(subvol[:,:, j*imgs_in_row+i], cmap=cmap_choice)
                    ax.set_title(f'z-slice {j*imgs_in_row+i}')

    title = f'{direction}-slices'
    f.suptitle(title, fontsize=12)

    if save_img:
        plt.savefig("slices.png")
        return

    #save to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(f)
    buf.seek(0)

    return buf


def render_3d_volume_plotly(subvol, direction='z', color_choice="jet", 
                            save_img=True):

    size_x, size_y, size_z = np.shape(subvol)

    X, Y, Z = np.mgrid[0:size_x, 0:size_y, 0:size_z]
    
    vol = go.Volume(
          x = X.flatten(),
          y = Y.flatten(),
          z = Z.flatten(),
          value = subvol.flatten(),
          opacity = 0.3,
          opacityscale = 0.3,
          surface_count = 10,
          colorscale=color_choice,
          isomax = 40000,
          #isomin = 20000,
          #slices_z = dict(show=True, locations=[10]),
        )
    fig = go.Figure(data=vol)


    def generate_ticks(axis, interval, size_um=None):
        vals=[]
        ticks =[]
    
        if not size_um:
            size_um=1
        for i in range(0, axis, interval):
            vals.append(i)
            ticks.append(i*size_um)
      
        return (vals, [str(tick) for tick in ticks])
    

    x_vals, x_ticks = generate_ticks(size_x, 8)
    y_vals, y_ticks = generate_ticks(size_y, 8)
    z_vals, z_ticks = generate_ticks(size_z, 8)
   
    if direction == 'x':
        up_direction = dict(x=1, y=0, z=0)
        eye = dict(x=1.25, y=1.25, z=1.25)
    elif direction == 'y':
        up_direction = dict(x=0, y=1, z=0)
        eye = dict(x=1.25, y=1.25, z=1.25)
    else: # directoin == 'z'
        up_direction = dict(x=0, y=0, z=1)
        eye = dict(x=-1.25, y=1.25, z=1.25)

    fig.update_layout(title="3D rendering",
                      scene = dict(
                        xaxis = dict(
                            ticktext=x_ticks,
                            tickvals=x_vals),
                        yaxis = dict(
                            ticktext=y_ticks,
                            tickvals=y_vals),
                        zaxis = dict(
                            ticktext=z_ticks,
                            tickvals=z_vals)),
                     scene_aspectmode='data',
                     scene_camera = dict(up=up_direction, eye=eye),
                     )
    if save_img:
        fig.write_image("3D_render.png")
        return

    plotly_bytes = fig.to_image(format="png")
    return io.BytesIO(plotly_bytes)


def create_summary(subvol, outfile):

    # Render 2D Images
    images = []
    for direction in ['x', 'y', 'z']:
        slice_img = render_slices(subvol, direction, save_img=False)
        images.append(slice_img)
    
    
    # Render 3D Images
    for direction in ['x', 'y', 'z']:
        plotly_img = render_3d_volume_plotly(subvol, direction, save_img=False)
        images.append(plotly_img)
    
    
    # Convert the byte arrays to viewable images and concatenate
    graphs = [Image.open(img) for img in images]
    print("image Files length: ", len(graphs))
    
    # At this point, there should be 6 images 
    
    img_size = [0,0] # (width, height)
    
    # Only up to the first plotly image for calculating 
    # as the other plotly images will be added to the side.
    # (3 plotly images side by side should be less than matplotlib 
    # image width)
    for graph in graphs[0:4]: 
        if graph.width > img_size[0]:
            img_size[0] = graph.width
        img_size[1] = img_size[1] + graph.height
        
    #print("width: ", img_width)
    #print("height: ", img_height)
    
    summary_img = Image.new('RGB', (img_size[0], img_size[1]))
    current_pos = [0,0]
    
    ##  Stitch all graphs together
    # Matplotlib images
    for graph in graphs[0:3]:
        summary_img.paste(graph,  current_pos)
        # bring the current position down by the pasted image's height
        current_pos = (0, current_pos[1] + graph.height)
    
    # Plotly images
    for graph in graphs[3:6]:
        summary_img.paste(graph, current_pos)
        # shift it to the side
        current_pos = (current_pos[0] + graph.width, current_pos[1])
    
    summary_img.save(outfile)
    
    for img in images:
        img.close()
    
        

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()

    parser.add_argument("--input_dir", help="path to input data directory")
    parser.add_argument("--outfile", help="output file path")
    args = parser.parse_args()

    input_data_dir = args.input_dir
    outfile = args.outfile

    subvol = get_data_array(input_data_dir)
    create_summary(subvol, outfile)
    
