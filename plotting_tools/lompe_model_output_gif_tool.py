#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 12:35:17 2023

@author: clevenger
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 23:42:22 2023

@author: clevenger
"""

import os
import imageio

# Directory/file path for images going in
directory_path = "/Users/clevenger/Projects/lompe_swarm/test_outputs"

# Output directory file name to append to path
output_gif = "output.gif"

# Store the images
images = []

# List all files in the directory
image_files = os.listdir(directory_path)

# Sort the files so they output in correct order
image_files.sort()

# Read and append each image to the storage list
for image_file in image_files:
    image_path = os.path.join(directory_path, image_file)
    if image_path.endswith(".png"):  # You can adjust the file extension as needed
        images.append(imageio.imread(image_path))

# Save the list of images as a GIF
imageio.mimsave(output_gif, images, duration=500)

print(f"GIF saved as {output_gif}")
