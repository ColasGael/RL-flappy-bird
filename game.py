import numpy as np
import matplotlib.pyplot as plt
import cv2

from util import *
from environment import Environment
from bird import Bird


class Game:
    
    def __init__(self, isHuman=True):
        self.params = game_parameters()
        self.bird = Bird()
        self.env = Environment(isHuman=isHuman, bird=self.bird)
        self.score = 0
        self.inGame = False
        self.hasJumped = False
    
    def fail(self):
        rows, cols, _ = self.bird.img.shape
        x_b, y_b = self.bird.x + self.env.pad - cols//2, max(self.bird.y + self.env.pad - rows//2, 0)
        
        isCollision = (self.env.occ[y_b:y_b + rows, x_b:x_b + cols]).any()
        
        return isCollision
    
    def play(self):

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        im = ax.imshow(self.env.map)
        plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
                
        def start_onclick(event):
            self.inGame = True
            
            while self.inGame:
                plt.pause(0.0001)
                if self.fail():
                    print("YOU DIED")
                    self.inGame = False
                    self.bird.img = jpg2numpy(self.params["explosion_sprite"], self.params["explosion_dims"])

                self.bird.move()

                self.env.scroll()
                im.set_data(self.env.map)
                plt.draw()
                self.hasJumped = False
    
        def jump_onkey(event):
            if (not self.inGame) or self.hasJumped:
                pass  
            elif event.key == "z":
                self.bird.jump()
                self.hasJumped = True
                
            if event.key == "n":
                self.__init__()
                self.inGame = False
                im.set_data(self.env.map)
                plt.draw()
            elif event.key == "q":
                plt.close()
            
        cid_start = fig.canvas.mpl_connect('button_press_event', start_onclick)
        cid_jump = fig.canvas.mpl_connect('key_press_event', jump_onkey)
        #fig.canvas.mpl_disconnect(cid)

        plt.show()
    
# method: is_collision (use occupancy grid)

if __name__ == '__main__':
    Game().play()
    
