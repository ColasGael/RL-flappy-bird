"""Define the class used to keep track of the state of the player (the bird).

Authors:
    Gael Colas
"""

import numpy as np

from util import *


class Bird:
    """Hero of the game.
    
    Attributes:
        'args' (ArgumentParser): parser gethering all the Game parameters
        'img' (np.array, shape=bird_dims): RGB-pixel array of the Bird sprite, resized to the standard shape 'bird_dims'
        'x' (int): row pixel coordinate of the Bird center in the environment
        'y' (int): column pixel coordinate of the Bird center in the environment
        't' (int): number of time steps since the last jump
        'score' (int): current score

    Remarks:
        'x' is fixed, only the environment moves by scrolling.
    """
    
    def __init__(self, args):
        super(Bird).__init__()
        self.args = args

        self.img = jpg2numpy(self.args.bird_sprite, self.args.bird_dims)
        self.x = self.args.bird_pos[0]
        self.y = self.args.bird_pos[1]
        
        self.t = int(self.args.v0 / self.args.a0)
    
    def jump(self):
        """Update the state of the bird to account for a new jump.
        """
        # update the number of times steps since the last jump 
        self.t = 0
    
    def move(self):  
        """Update the state of the bird after 1 time step move.
        """
        # update the number of times steps since the last jump 
        self.t += 1
        
        # new y-coordinate of the bird after the move
        self.y -= max(self.t*self.args.v0 -0.5*self.t**2*self.args.a0 + (self.t < 5)*self.args.dy, -self.args.v_max)
        # convert to int
        self.y = max(int(self.y), 0)
