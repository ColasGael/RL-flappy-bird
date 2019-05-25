import numpy as np
import cv2


def jpg2numpy(im_path, im_dims):
    """Load a JPG image into a numpy array and reshape it to the correct dimensions.
    
    Args:
        'im_path' (Path): path to the JPG image
        'im_dims' (tuple: (rows, cols)): dimensions of the output array
    
    Return:
        'im_array' (np.array, shape=(im_dims,3), dtype=int): corresponding array of RGB-pixels
    """
    # read image into numpy array
    im_array = cv2.imread(im_path)
    # resize to match dimension requirements: OpenCV convention (cols, rows)
    im_array = cv2.resize(im_array, dsize=(im_dims[1], im_dims[0]), interpolation=cv2.INTER_CUBIC)
    # convert from OpenCV BGR to RGB pixel convention
    im_array = np.flip(im_array, axis=-1)
    
    return im_array
    
    
def game_parameters():
    """Return a dictionary gethering all the Game hyperparameters.
    
    Return:
        params (dict): dictionary gethering all the Game hyperparameters
    """
    params = {}
    # Objects dimensions in pixels
        # window
    params["window_size"] = (370, 240) 
    params["padding"] = 5
        # environment
    params["ground_height"] = 64
    params["pipe_width"] = 40
    params["pipe_dist"] = (90, 80) # (x,y)-distance
    params["pipe_min_height"] = 10
        # bird
    params["bird_dims"] = (20, 20)  
    params["bird_pos"] = (80, 150) # (x,y)-position
        # explosion
    params["explosion_dims"] = (50, 50)

    # Dynamics (bird movement) hyperparameters
    params["v0"] = 0.4
    params["a0"] = 0.3
    params["dt"] = 10
    params["v_max"] = 3
    params["dv"] = 2
    
    # Sprites to use
    params["bg_sprite"] = "sprites/bg_fb.jpg"
    params["floor_sprite"] = "sprites/floor_fb.jpg"
    params["pipe_sprite"] = "sprites/pipe_fb.jpg"
    params["bird_sprite"] = "sprites/bird_rocket.jpg"
    params["explosion_sprite"] = "sprites/explosion.jpg"
    
    return params
    


