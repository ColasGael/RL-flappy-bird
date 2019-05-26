"""Useful functions for the Game.

Authors:
    Gael Colas
"""

import numpy as np
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
    
    



