#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 30 16:34:17 2023

@author: clevenger
"""

import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.animation import FuncAnimation

# Load the GIFs
gif1 = Image.open('/Users/clevenger/Projects/lompe_pfisr/test_scripts/output.gif')
gif2 = Image.open('/Users/clevenger/Projects/lompe_pfisr/test_scripts/output_vvels.gif')

# Create subplots
fig, (ax1, ax2) = plt.subplots(1, 2)

# Turn off axis labels and ticks
ax1.axis('off')
ax2.axis('off')

im1=ax1.imshow(gif1)
im2=ax2.imshow(gif2)

# Display the GIFs
#ax1.imshow(gif1)
#ax2.imshow(gif2)

def update(frame):
    gif1.seek(frame)
    gif2.seek(frame)
    im1.set_data(gif1)
    im2.set_data(gif2)

#fig,(ax1,ax2)=plt.subplots(1,2)
num_frames=min(gif1.n_frames,gif2.n_frames)
animation=FuncAnimation(fig,update,frames=range(num_frames),repeat=True)

# Show the combined figure
#plt.show()

animation.save('combined.gif',writer='pillow',fps=2)