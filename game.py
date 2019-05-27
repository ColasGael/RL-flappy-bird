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
from agent import AIAgent

class Game:
    """Class defining the Game framework.
    
    Attributes:
        'args' (ArgumentParser): parser gethering all the Game parameters
        'bird' (Bird, default=None): the Bird
        'env' (Environment): the game Environment
        
        'score' (int): current score
        'highscore' (tuple of int, (human, AI)): the best score achieved by a human and an AI
        'inGame' (bool): indicates if we are currently playing the Game
        'hasJumped' (bool): indicates if an action (jumping) as been made at the current time step
        't' (int): number of time steps since the beginning of the game
        
        'isHuman' (bool, default=True): whether a human or an AI is playing the Game
        'agent' (AIAgent, default=None): AI agent playing the game
        'muteDisplay' (bool, default=False): whether or not to mute the display of the frames
    """
    
    def __init__(self, args):
        super(Game).__init__()
        self.args = args
        
        # environment parameters
        self.bird = Bird(args)
        self.env = Environment(args, bird=self.bird)
        
        # game parameters
        self.score = 0
        self.highscore = load_highscore(args.highscore_filename)
        self.inGame = False
        self.hasJumped = False
        self.t = 0
        
        # to play with an AI
        self.isHuman = (args.agent == "human")
        if not self.isHuman:
            state = self.env.get_state()
            self.agent = AIAgent(args, state)
            # load saved parameters
            if self.args.load_save:
                load_agent(self.agent, self.args.save_filename)
            
        self.muteDisplay = False

            
    def reset(self):
        """Reset the environment and the bird position to start a new game.
        """
        #print(self.agent.n_sim, self.score)
        # update the highscore if needed
        if self.isHuman and (self.score > self.highscore[0]):
            self.highscore[0] = self.score
            update_score(self.highscore, self.args.highscore_filename)
        elif (not self.isHuman) and (self.score > self.highscore[1]):
            self.highscore[1] = self.score
            update_score(self.highscore, self.args.highscore_filename)
            
        # reset the simulation
        self.bird = Bird(args)
        self.env = Environment(args, bird=self.bird)
        self.score = 0
        self.inGame = False
        self.hasJumped = False
        self.t = 0
        
        # update the state of the agent
        if not self.isHuman:
            state = self.env.get_state()
            self.agent.reset(state)
        
        # update the image 
        if not self.muteDisplay:
            self.im.set_data(self.env.map)
            display_info(self.score, self.highscore, text_handle=self.text_score)  
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
        """Update the score when the middle of a pipe is crossed.
        
        Return:
            'isCrossed' (bool): indicate that the middle of the next pipe has been crossed
        """
        isCrossed = np.any([self.bird.x  == (pipe[0] + self.args.pipe_width//2) for pipe in self.env.pipes])
        
        if isCrossed:
            # update the score
            self.score += 1
            # display the new score
            if not self.muteDisplay:
                display_info(self.score, self.highscore, text_handle=self.text_score)  
                
        return isCrossed
    
    def step(self):
        """Play one time step in the game.
        """
        # update the score
        isScoreUpdated = self.update_score()
        
        # the player hit an obstacle
        isFail = self.fail()
        if isFail:
            self.inGame = False
            # display an explosion instead of the bird image
            self.bird.img = jpg2numpy(self.args.explosion_sprite, self.args.explosion_dims)

        # if the AI is playing: take an action
        if not self.isHuman:
            self.agent.choose_action()     
            
        # compute the new bird position
        self.bird.move()
 
        # scroll 1 frame and generate the new environment
        new_state = self.env.scroll()
       
        # if the AI is playing: set the new state
        if not self.isHuman:
            # get the new_state
            new_state = self.env.get_state()
            # feed the transition information to the agent
            self.agent.set_transition(new_state, isScoreUpdated, isFail) 
            
        # only display 1 every 2 time frames for fluidity
        if ((self.t % 2 == 0) or self.fail()) and not self.muteDisplay:
            # change the displayed image to account for changes
            self.im.set_data(self.env.map)
            # update the image without pausing
            plt.draw()
            
        # new time step
        self.t += 1
        self.hasJumped = False
                
    def play(self):
        """Launch a game.
        
        Commands:
            LEFT-CLICK : start
            SPACE : jump
            N : reset game
            M : mute display
            Z : save AI data
            Q : quit
        """ 
        # get useful handles
        fig = plt.figure()
        ax = fig.add_subplot(1, 2, 1)
        self.im = ax.imshow(self.env.map)
        # to hide tick values on X and Y axis
        plt.xticks([]), plt.yticks([]) 
        # display the commands and the current score
        self.text_score = display_info(self.score, self.highscore, coord=self.args.window_size, commands_filename=self.args.commands_filename)
        
        # left-click mpl event: start the game
        def start_onclick(event):
            self.inGame = True
            
            # while the player does not fail
            while self.inGame:
                # safe way to pause a plt animation
                plt.pause(1e-3)
                self.step()
                
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
            # quit the game if Q is pressed
            elif event.key == "q":
                plt.close()
            # mute the display if M is pressed
            elif event.key == "m":
                self.muteDisplay = not self.muteDisplay
            # save the AI agent parameters if S is pressed
            elif event.key == "z":
                if not self.isHuman:
                    save_agent(self.agent, self.args.save_filename)
            
        # right click to start the game
        cid_start = fig.canvas.mpl_connect('button_press_event', start_onclick)
        # keyboard input to interact with the game
        cid_jump = fig.canvas.mpl_connect('key_press_event', jump_onkey)
        
        # disconnect the events
        if False:
            fig.canvas.mpl_disconnect(cid_start)
            fig.canvas.mpl_disconnect(cid_jump)
        
        # display the game
        plt.show()
    

if __name__ == '__main__':
    # get arguments needed to play the Game
    args = get_game_args()
    # launch the game
    Game(args).play()
    
