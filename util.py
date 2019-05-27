"""Useful functions for the Game.

Authors:
    Gael Colas
"""

import numpy as np
import matplotlib.pyplot as plt
import cv2
import ujson as json


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
    
    # check that an image has been loaded
    if im_array is None:
        raise FileNotFoundError("The image {} does not exist.".format(im_path))
    
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
    
    mask = (im_array[:,:,1] < 100) | (im_array[:,:,0] >= im_array[:,:,1]) | (im_array[:,:,2] >= im_array[:,:,1]) 
    
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
    
    # try opening the highscore file
    try:
        highscore_file = open(highscore_filename, "r")
        
        # if the file exists, read the score from it
        for line in highscore_file.readlines():
            name, score = line.split(" ")
            
            if "human" in name:
                human_score = int(score)
            elif "ai" in name:
                ai_score = int(score)
        
    except FileNotFoundError:
        print("No highscore file '{}' found. Creating a new one...".format(highscore_filename))
        open(highscore_filename, "w")
    
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
        
def save_agent(agent, out_filename):
    """Save the agent parameters to a JSON file.
    
    Args:
        'agent' (AIAgent): AI agent to save
        'out_filename' (str): name of the output file
    """
    with open(out_filename, "w") as out_file:
        json.dump(agent.mdp_data, out_file)
    
    print("The AI agent has been saved to: {}".format(out_filename))
    
def load_agent(agent, in_filename):
    """Load the saved agent parameters from a JSON file.
    
    Args:
        'agent' (AIAgent): AI agent to load the parameters into
        'in_filename' (str): name of the input file
    """
    with open(in_filename, "r") as in_file:
        mdp_data = json.load(in_file)
    
    # convert all the list to np.arrays
    agent.mdp_data = {
        'num_states': mdp_data['num_states'],
        'state_discretization': [np.array(states_list) for states_list in mdp_data['state_discretization']],
        'transition_counts': np.array(mdp_data['transition_counts']),
        'transition_probs': np.array(mdp_data['transition_probs']),
        'reward_counts': np.array(mdp_data['reward_counts']),
        'reward': np.array(mdp_data['reward']),
        'value': np.array(mdp_data['value'])
    }
    print("The AI agent has been loaded from: {}".format(in_filename))
