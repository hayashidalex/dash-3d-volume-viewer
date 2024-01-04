# Dash Volume Viewer

## Purpose
For firing up an interactive volumetric data viewer on a browser. Volumes can be
viewed as (matplotlib) slices on 3 directions (x,y,z) and as a (Dash/Plotly)
3D rendering.

## Usage

### Set up the environment

Use of python virtual environment is recommended

```
python -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
```

### Start the app

Run the app with
```
python app.py
```
Then, on your browser, go to `http://127.0.0.1:8050/`

### Load data
Input data should be in one of the two formats: 

1. numpy array saved as a binary file (`.npy`)
2. a directory containing tiff image stacks for the volume

In both cases, enter the path to the file (or the directory in the second case).
Once you click Submit, it will automatically start displaying 2D slices. 

Download buttons are for generating .png files of the displayed images.

## Limitations
3D rendering can hang or crash especially when the surface count is large. 

## Tested Python Versions
3.9, 3.10

# (Additional file) Stand alone module 
`subvolume_visualization.py`  can be used for generating renderings 
non-interactively

