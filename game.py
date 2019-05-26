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
        self.t = 0
    
    def reset(self, im, text_score):
        """Reset the environment and the bird position to start a new game.
        """
        self.__init__(self.args)
        im.set_data(self.env.map)
        text_score.set_text("SCORE: {}\n".format(self.score))
        plt.draw()
    
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
    
    def update_score(self):
        """Update the score when a pipe is crossed.
        """
        return np.any([self.bird.x == pipe[0] for pipe in self.env.pipes])
    
    def step(self, im, text_score):
        """Play one time step in the game.
        """
        # update the score
        if self.update_score():
            self.score += 1
            # display the new score
            text_score.set_text("SCORE: {}\n".format(self.score))
        
        # the player hit an obstacle
        if self.fail():
            self.inGame = False
            # display an explosion instead of the bird image
            self.bird.img = jpg2numpy(self.args.explosion_sprite, self.args.explosion_dims)

        # compute the new bird position
        self.bird.move()
        # scroll 1 frame and generate the new environment
        self.env.scroll()
        
        # only display 1 every 2 time frames for fluidity
        if (self.t % 2 == 0) or self.fail():
            # change the displayed image to account for changes
            im.set_data(self.env.map)
            # update the image without pausing
            plt.draw()
            
        # new time step
        self.t += 1
        self.hasJumped = False
                
    def play(self):
        """Launch a game.
        
        Commands:
            RIGHT-CLICK : start new game
            SPACE : jump
            N : reset game
            Q : quit
        """ 
        # get useful handles
        fig = plt.figure()
        ax = fig.add_subplot(1, 2, 1)
        im = ax.imshow(self.env.map)
        # to hide tick values on X and Y axis
        plt.xticks([]), plt.yticks([]) 
        # display the commands and the current score
        text_score = display_score_commands(self.args.window_size, self.score, self.args.commands_filename, ax)
        
        # right click mpl event: start the game
        def start_onclick(event):
            self.inGame = True
            
            # while the player does not fail
            while self.inGame:
                # safe way to pause a plt animation
                plt.pause(1e-30)
                self.step(im, text_score)
                
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
                self.reset(im, text_score)
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
    
