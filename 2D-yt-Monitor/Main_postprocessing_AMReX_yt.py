#-----------------------------------------------------------------------------------------
# Project                       : Postprocessing the AMReX plotfile with yt
# Postprocessing_AMReX_yt       : The main function
# Programer                     : Shanqin Jin
# Note                          : You need to run the command "conda activate pyamrex"
# Date                          : 2025-07-06
#-----------------------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pyright: reportPrivateImportUsage=false

import os
import re
import argparse  # for command line arguments, e.g. python Main_postprocessing_AMReX_yt.py --var density --axis z --dir .
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_agg import FigureCanvasAgg
from sympy import all_roots
import yt
import json
import time
import math
import sys
import imageio.v2 as imageio    # type: ignore


#-----------------------------------------------------------------------------------------
# set matplotlib formatting to be the same as yt
plt.rcParams['font.size'] = 16
plt.rcParams['font.family'] = 'serif'
plt.rcParams['mathtext.fontset'] = 'stix'
#-----------------------------------------------------------------------------------------



#-----------------------------------------------------------------------------------------
current_dir = os.path.dirname(__file__)     # Get the current directory and the parent directory
parent_dir = os.path.dirname(current_dir)   # The parent directory of the current directory

# Parameters
debug_or_release = 0   # 1: Debug, 0: Release
plotfile_dir = os.path.join(parent_dir, "output")
layout_rows = 1                                                 # The number of rows in the subplot layout
var_name = ["phi", "analytical_phi", "dphidx"]                  # The variables to be plotted
titles = [
    r'$\phi$',
    r'$\phi_{\mathrm{analytical}}$',
    r'$\frac{\partial \phi}{\partial x}$'
]
var_color_range = [[-2.0, 2.0], [-2.0, 2.0], [-10.0, 10.0]]     # The range of the color map
# The color map, color map types: viridis, hot_r, plasma, magma, seismicetc.
# Rainbow, rainbow
color_map = ["viridis", "hot_r", "rainbow"]                       
time_label_position = [0.5, 0.96]                               # The position of the time label


refresh_interval = 0.5                                          # The interval of checking the new plotfile

# # Checking 5 subplots
# layout_rows = 2                                                 # The number of rows in the subplot layout
# var_name = ["phi", "analytical_phi", "dphidx", "dphidx", "dphidx"]                  # The variables to be plotted
# titles = ["phi", "analytical_phi", "dphidx", "dphidx", "dphidx"]                    # The titles of the plots
# var_color_range = [[-2.0, 2.0], [-2.0, 2.0], [-10.0, 10.0], [-10.0, 10.0], [-10.0, 10.0]]     # The range of the color map
# color_map = ["viridis", "hot_r", "hot_r", "hot_r", "hot_r"]                         # The color map, color map types: viridis, hot_r, etc.
# refresh_interval = 0.5                                          # The interval of checking the new plotfile

# # Checking 1 subplots
# layout_rows = 1                                                 # The number of rows in the subplot layout
# var_name = ["phi"]                  # The variables to be plotted
# titles = ["phi"]                    # The titles of the plots
# var_color_range = [[-2.0, 2.0]]     # The range of the color map
# color_map = ["viridis"]                         # The color map, color map types: viridis, hot_r, etc.
# refresh_interval = 0.5                                          # The interval of checking the new plotfile


# The folders that have been processed
processed_folders = set()  


# Release mode: load the parameters from the postprocessing_Setup.json
if debug_or_release == 0:
    with open("postprocessing_Setup.json", "r") as f:
        setup = json.load(f)
    
    plotfile_dir        = os.path.join(parent_dir, setup["plotfile_dir"])
    var_name            = setup["var_name"]
    titles              = setup["titles"]
    layout_rows         = setup["layout_rows"]
    var_color_range     = setup["var_color_range"]
    color_map           = setup["color_map"]
    time_label_position = setup["time_label_position"]

subplot_number = len(var_name)
figure_size=[5 *  math.ceil(subplot_number / layout_rows), 3.5 * layout_rows]
if len(var_name) != len(var_color_range):
    raise ValueError("The number of variables and the number of color ranges must be the same")
    sys.exit()
#-----------------------------------------------------------------------------------------



#-----------------------------------------------------------------------------------------
def yt_plot(folder_path):

    # Load the plotfile
    print(f"\n")
    print(f"#------------------------------------------------------------------------------------------------")
    print(f"Reading the new folder: {folder_path}")

    # List the files in the folder
    for fname in os.listdir(folder_path):
        print("  -", fname)

    debug_folder = os.path.join(os.path.dirname(__file__), "debug_results", os.path.basename(folder_path))
    os.makedirs(debug_folder, exist_ok=True)

    #-------------------------------------------------------------------------------------
    # Load the plotfile
    ds = yt.load(folder_path)
    latest_plt = os.path.basename(folder_path)
    current_time = ds.current_time  # AMReX plotfile time

    # print out fields available for plotting
    print(ds.field_list)

    # Plot the data with yt
    for i, var in enumerate(var_name):

        vmin, vmax = var_color_range[i]
        
        slc = yt.SlicePlot(ds, 'z', ('boxlib', var), center=[0.5, 0.5, 0.0], buff_size=(800, 800))
        slc.set_font_size(35)  # Set the font size
        slc.set_log(('boxlib', var), False)
        slc.set_cmap(('boxlib', var), color_map[i])  # Set the color map, color map types: viridis, hot_r, etc.
        slc.set_colorbar_label(('boxlib', var), titles[i])  # Set the colorbar label

        # # Set the timestamp and scale
        # slc.annotate_timestamp(corner="upper_left", redshift=True, draw_inset_box=True) # type: ignore
        # slc.annotate_scale(corner="upper_right") # type: ignore

        # Set the color map limits
        slc.set_zlim(('boxlib', var), zmin=vmin, zmax=vmax)
            
        # # Set the title
        # fig.annotate_title("CIP method")                                     # type: ignore

        # Set the grids and cell edges
        # fig.annotate_grids(linewidth=2, alpha=1, edgecolors='red')           # type: ignore
        slc.annotate_cell_edges(line_width=0.0005, alpha=0.4, color='white') # type: ignore 

        # # matplotlib figure from yt
        # mat_fig = fig.plots[('boxlib', 'phi')].figure
        # mat_fig.savefig("phi_slice.eps", format='eps', dpi=300)

        # Save the plot
        figure_path = os.path.join(debug_folder, 'subplot', f"{latest_plt}_{var}.png")
        slc.save(figure_path)

    return current_time
    #-------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------




#-----------------------------------------------------------------------------------------
def combine_plots(folder_path, current_time):

    # Load the plotfile
    print(f"\n")
    print(f"# Combining the plots into a single figure...")

    # Get the image paths
    latest_plt = os.path.basename(folder_path)
    image_paths = [os.path.join(os.path.dirname(__file__), "debug_results", latest_plt, 'subplot', f"{latest_plt}_{var}.png") for var in var_name]

    # Combine the plots into a single figure using matplotlib
    n_images = len(image_paths)
    n_cols = math.ceil(n_images / layout_rows)
    img_w, img_h = 1.0 / n_cols, 1.0 / layout_rows  # The width and height of each subplot

    fig = plt.figure(figsize=(figure_size[0], figure_size[1]))

    for idx, img_path in enumerate(image_paths):
        row = idx // n_cols
        col_in_row = idx % n_cols

        # The last row special treatment: center
        if row == layout_rows - 1 and n_images % n_cols != 0:
            actual_cols_last_row = n_images % n_cols
            left_offset = (n_cols - actual_cols_last_row) / 2
            col = left_offset + col_in_row
        else:
            col = col_in_row

        # Calculate the subplot position: [left, bottom, width, height]
        left = col * img_w
        bottom = 1.0 - (row + 1) * img_h - 0.02
        ax = fig.add_axes([left, bottom, img_w * 1.0, img_h * 0.95]) # type: ignore

        # Read the image
        img = mpimg.imread(img_path)
        ax.imshow(img)
        ax.axis('off')

        # # Set the title
        # if titles and idx < len(titles): ax.set_title(titles[idx], fontsize=16)

    # Adjust the spacing between subplots
    plt.subplots_adjust(hspace=0.1, wspace=0.1)

    combined_image_paths = os.path.join(os.path.dirname(__file__), "debug_results", latest_plt, f"{latest_plt}_combined.png")
    

    # Add the time label to the figure
    time_label = f"Simulation time: t = {float(current_time):.3f} s"
    fig.text(time_label_position[0], time_label_position[1], time_label, ha='center', fontsize=12)

    fig.savefig(combined_image_paths, dpi=300)
    # plt.show()

    return fig
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Convert the matplotlib Figure to a numpy RGB image array
# def figure_to_array(fig):
#     canvas = FigureCanvasAgg(fig)
#     canvas.draw()
#     w, h = canvas.get_width_height()
#     buf = canvas.buffer_rgba()
#     img = np.frombuffer(buf, dtype=np.uint8).reshape(h, w, 4)
#     return img[:, :, :3]  # Only RGB, no Alpha channel


from io import BytesIO
from PIL import Image

def figure_to_array(fig, dpi=300):
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    img = Image.open(buf).convert('RGB')  # 去除 alpha
    return np.asarray(img)

#-----------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------
def main():

    print(f"Starting monitoring the directory: {plotfile_dir}")

    frames = []  # For storing each frame image

    # Create a display window
    plt.ion()  # Open interactive mode
    fig_display, ax_display = plt.subplots(figsize=(figure_size[0], figure_size[1]))

    # Running forloop to check the target folder has the new plotfile or not
    # Find the latest plotfile in the plotfile directory
    while True:
        try:
            all_folders = sorted([f for f in os.listdir(plotfile_dir) if f.startswith("plt")])

            new_folders = [f for f in all_folders if f not in processed_folders]

            for folder in sorted(new_folders):
                folder_path = os.path.join(plotfile_dir, folder)
                
                # Plot the data with yt
                current_time = yt_plot(folder_path)

                # Combine the plots into a single figure using matplotlib
                Combined_Figure = combine_plots(folder_path, current_time)

                # Convert the combined figure to an image frame and add it to the frames list
                try:

                    frame = figure_to_array(Combined_Figure, dpi= 300)
                    frames.append(frame)
                    # Convert the combined figure to a numpy image and display it in the existing window
                    ax_display.clear()
                    ax_display.imshow(frame)
                    ax_display.axis("off")
                    plt.pause(0.1)   # Refresh the image after 0.1 second

                except Exception as e:
                    print(f"[Warning]: Could not convert figure to image: {e}")
                finally:
                    plt.close(Combined_Figure)  # Release memory


                # Add the folder to the processed folders
                processed_folders.add(folder)  

            # Wait for the next check
            time.sleep(refresh_interval)

        except KeyboardInterrupt:
            print("\nMonitoring stopped.")

            # Save the frames as a GIF
            if frames:
                gif_path = os.path.join(os.getcwd(), "debug_results", "simulation.mp4") # you can save .gif; .mp4; .webm.
                imageio.mimsave(gif_path, frames, fps=2)
                print(f" GIF saved to {gif_path}")

            break
        except Exception as e:
            print(f"[ERROR]:{e}")
            time.sleep(refresh_interval)

#-----------------------------------------------------------------------------------------






#-----------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
