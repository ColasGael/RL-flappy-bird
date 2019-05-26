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
    
def display_info(score, highscore, coord=(0, 0), commands_filename=None, text_handle=None):
    """Display the commands and the current score
    
    Args:
        'coord' (tuple, (y, x)): pixel coordinates of the text box's bottom-left 
        'score' (int): current score
        'highscore' (tuple of int, (human, AI)): the best score achieved by a human and an AI
        'commands_filename' (str): filename of the text file listing the commands used in the game
        'text_handle' (Text Handle, default=None): text handle
        
    Return:
        'text_handle' (Text Handle): text handle
        
    Remarks:
        If the 'text_handle' is given, then we update the text instead of replotting it.
    """
    score_text = "SCORE: {}\n\n Highscore Human: {}\n Highscore AI: {}\n".format(score, *highscore)
    
    # check if update the score
    if text_handle is not None:
        text_handle.set_text(score_text)
    
    # otherwise, we plot the text for the first time
    else:        
        with open(commands_filename, "r") as commands_file:
            commands_text = commands_file.read()
            
        plt.text(coord[1] + 20, coord[0], commands_text, fontsize=14)
        text_handle = plt.text(coord[1] + 20, coord[0] - 200, score_text, fontsize=20)
    
    return text_handle
    
def load_highscore(highscore_filename):
    """Load the highscore stored in a text file.
    
    Args:
        'highscore_filename' (str): filename of the highscore text file
    
    Return:
        'highscore' (tuple of int, (human, AI)): the best score achieved by a human and an AI
    """
    human_score, ai_score = -1, -1
    
    with open(highscore_filename, "r") as highscore_file:
        lines = highscore_file.readlines()
        
        for line in lines:
            name, score = line.split(" ")
            
            if "human" in name:
                human_score = int(score)
            elif "ai" in name:
                ai_score = int(score)
    
    highscore = [human_score, ai_score]
    
    return highscore

def update_score(highscore, highscore_filename):
    """Update the highscore text file with the new highscore.
    
    Args:
        'highscore' (tuple of int, (human, AI)): the best score achieved by a human and an AI
        'highscore_filename' (str): filename of the highscore text file
    """
    with open(highscore_filename, "w") as highscore_file:
        highscore_file.write("human {}\nai {}".format(highscore[0], highscore[1]))
    


