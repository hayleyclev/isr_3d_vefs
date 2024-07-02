#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 23:42:22 2023

@author: clevenger
"""

import imageio
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import numpy as np

# List of image file paths for the static subplots
static_image_paths = [
    "/path/to/static_image1.png",
    "/path/to/static_image2.png",
    "/path/to/static_image3.png",
    "/path/to/static_image4.png",
]

# List of image file paths in the order you want them in the GIF (for the moving GIF)
moving_image_paths = [
    "/Users/clevenger/Projects/lompe_pfisr/test_outputs/2017-06-16_140100.png",
    # Add the paths for other frames as needed
]

# Output GIF file name
output_gif = "combined_output.gif"

# Create a list to store images
images = []

# Read and append each static image to the list
for image_path in static_image_paths:
    images.append(imageio.imread(image_path))

# Parameters for the vertical line
vertical_line_time = datetime.datetime(2017, 6, 16, 14, 1, 0)
vertical_line_color = 'magenta'
vertical_line_linestyle = '--'

# Loop through the frames of the existing moving GIF
for image_path in moving_image_paths:
    # Read the frame from the existing GIF
    moving_frame = imageio.imread(image_path)
    
    # Create a new figure with two subplots (1 row, 2 columns)
    fig, axarr = plt.subplots(1, 2, figsize=(12, 6))

    # Plot the moving frame on the left
    axarr[0].imshow(moving_frame)
    
    # Plot the static subplots on the right
    for i, static_image in enumerate(images):
        axarr[1].imshow(static_image)
    
    # Add the vertical line to both subplots
    axarr[0].axvline(x=mdates.date2num(vertical_line_time), color=vertical_line_color, linestyle=vertical_line_linestyle)
    axarr[1].axvline(x=mdates.date2num(vertical_line_time), color=vertical_line_color, linestyle=vertical_line_linestyle)
    
    # Remove axes and labels for a cleaner look (adjust as needed)
    axarr[0].axis('off')
    axarr[1].axis('off')
    
    # Append the frame to the list of images
    images.append(np.asarray(fig))

    # Close the figure to prevent memory leaks
    plt.close(fig)

# Save the list of images as a GIF
imageio.mimsave(output_gif, images, duration=1)

print(f"GIF saved as {output_gif}")



