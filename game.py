"""Framework of the Game.

Authors:
    Gael Colas
"""

import numpy as np
import matplotlib.pyplot as plt
import cv2

from util import *
from args import get_game_args
from environment import Environment
from bird import Bird


class Game:
    """Class defining the Game framework.
    
    Attributes:
        'args' (ArgumentParser): parser gethering all the Game parameters
        'isHuman' (bool, default=True): whether a human or an AI is playing the Game
        'bird' (Bird, default=None): the Bird
        'env' (Environment): the game Environment
        'score' (int): current score
        'inGame' (bool): indicates if we are currently playing the Game
        'hasJumped' (bool): indicates if an action (jumping) as been made at the current time step
    """
    
    def __init__(self, args):
        self.args = args
        self.isHuman = (args.agent == "human")
        self.bird = Bird(args)
        self.env = Environment(args, bird=self.bird)
        self.score = 0
        self.inGame = False
        self.hasJumped = False
    
    def reset(self):
        """Reset the environment and the bird position to start a new game.
        """
        self.__init__(self.args)
    
    def fail(self):
        """Check if we failed the current game.
        
        Return:
            'isCollision' (bool): indicates if we encountered an obstacle.
        """
        rows, cols, _ = self.bird.img.shape
        # find the top-left coordinates of bird image
        x_b, y_b = self.bird.x + self.env.pad - cols//2, max(self.bird.y + self.env.pad - rows//2, 0)
        
        # check if the bird square intersects with some environment obstacles
        isCollision = (self.env.occ[y_b:y_b + rows, x_b:x_b + cols]).any()
        
        return isCollision
    
    def play(self):
        """Launch a game.
        
        Commands:
            RIGHT-CLICK : start new game
            N : reset game
            SPACE : jump
            Q : quit
        """ 
        # right click mpl event: start the game
        def start_onclick(event):
            self.inGame = True
            
            # while the player does not fail
            while self.inGame:
                # safe way to pause a plt animation
                plt.pause(0.0001)
                # the player hit an obstacle
                if self.fail():
                    self.inGame = False
                    # display an explosion instead of the bird image
                    self.bird.img = jpg2numpy(self.args.explosion_sprite, self.args.explosion_dims)

                # compute the new bird position
                self.bird.move()
                # scroll 1 frame and generate the new environment
                self.env.scroll()
                # change the displayed image to account for changes
                im.set_data(self.env.map)
                # update the image without pausing
                plt.draw()
                # new time step
                self.hasJumped = False
                
        # keyboard pressed mpl event
        def jump_onkey(event):
            # cannot jump if you already did for this time step or if you are not playing
            if (not self.inGame) or self.hasJumped:
                pass  
            # jump if SPACE is pressed
            elif event.key == " ":
                self.bird.jump()
                self.hasJumped = True
            
            # reset the game if N is pressed
            if event.key == "n":
                self.reset()
                self.inGame = False
                im.set_data(self.env.map)
                plt.draw()
            # quit the game if Q is pressed
            elif event.key == "q":
                plt.close()
            
        # right click to start the game
        cid_start = fig.canvas.mpl_connect('button_press_event', start_onclick)
        # keyboard input to interact with the game
        cid_jump = fig.canvas.mpl_connect('key_press_event', jump_onkey)
        
        # disconnect the event 'cid'
        #fig.canvas.mpl_disconnect(cid)
        
        # display the game
        plt.show()
    

if __name__ == '__main__':
    # get arguments needed to play the Game
    args = get_game_args()
    # launch the game
    Game(args).play()
    
