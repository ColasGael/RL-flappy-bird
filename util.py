"""Useful functions for the Game.

Authors:
    Gael Colas
"""

import numpy as np
import matplotlib.pyplot as plt
import cv2


def jpg2numpy(im_path, im_dims):
    """Load a JPG image into a numpy array and reshape it to the correct dimensions.
    
    Args:
        'im_path' (Path): path to the JPG image
        'im_dims' (tuple: (rows, cols)): dimensions of the output array
    
    Return:
        'im_array' (np.array, shape=(im_dims,3)): corresponding array of RGB-pixels
    """
    # read image into numpy array
    im_array = cv2.imread(im_path)
    # resize to match dimension requirements: OpenCV convention (cols, rows)
    im_array = cv2.resize(im_array, dsize=(im_dims[1], im_dims[0]), interpolation=cv2.INTER_CUBIC)
    # convert from OpenCV BGR to RGB pixel convention
    im_array = np.flip(im_array, axis=-1)
    
    return im_array
    
def green_screen(im_array):
    """Find which pixels of an input image correspond to an object on a green screen.
    
    Args:
        'im_array' (np.array, shape=(im_dims,3)): RGB-pixels array of input image
    
    Return:
        'mask' (np.array, shape=(im_dims), dtype=bool): boolean mask indicating the non-green screen pixels.
    """
    
    mask = (im_array[:,:,1] < 100) | (im_array[:,:,0] > im_array[:,:,1]) | (im_array[:,:,2] > im_array[:,:,1]) 
    
    return mask
    
def display_info(coord, score, commands_filename, ax):
    """Display the commands and the current score
    
    Args:
        'coord' (tuple, (y, x)): pixel coordinates of the text box's bottom-left 
        'score' (int): current score
        'commands_filename' (str): filename of the text file listing the commands used in the game
        'ax' (Axis): axis handle to use to display the text
        
    Return:
        'text_handle' (Text Handle): text handle
    """
    
    score_text = "SCORE: {}\n".format(score)
    
    with open(commands_filename, "r") as commands_file:
        commands_text = commands_file.read()
        
    ax.text(coord[1] + 50, coord[0], commands_text, fontsize=14)
    text_handle = ax.text(coord[1] + 50, 50, score_text, fontsize=20)
    
    return text_handle
   



