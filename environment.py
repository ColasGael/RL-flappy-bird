"""Define the class used to update and render the game environment.

Authors:
    Gael Colas
"""

import numpy as np
import matplotlib.pyplot as plt
import cv2

from util import *
from args import get_game_args


class Environment:
    """Class to update and generate the game environment.
    
    Attributes:
        'args' (ArgumentParser): parser gethering all the Game parameters
        'isHuman' (bool, default=True): whether a human or an AI is playing the Game
        'bird' (Bird, default=None): the Bird
        'bg_img' (np.array, shape=(window_size[0]-ground_height, window_size[1])): RGB-pixel array representing the background image
        'floor_img'(np.array, shape=(ground_height, window_size[1])): RGB-pixel array representing the floor image
        'pipe_img' (np.array, shape=(window_size[0], pipe_width)): RGB-pixel array representing a pipe facing up
        'pipe_img_rot' (np.array, shape=(window_size[0], pipe_width)): RGB-pixel array representing a pipe facing down
        'pipes' (list of tuple, (x, height)): list of all the current pipes in the environment 
                    (x = coord of front of pipe ; height = height of bottom pipe)
        'map' (np.array, shape=window_size, dtype=int): RGB-pixel array representing the full environment
        'occ' (np.array, shape=window_size, dtype=int): occupancy grid = binary matrix indicating the presence of obstacles
                    occ[i,j] = 1 if pixel (i,j) represents an obstacle, 0 otherwise
    
    Remarks:
        The object images are resized to the expected size as specified in 'args'.
        A new pipe is generated when the front one leave the screen. The height of the new pipe is randomly generated.
    """

    def __init__(self, args, bird=None):
        super(Environment).__init__()
        
        # load the Game parameters
        self.args = args
        # check whether a human or an AI is playing the Game
        self.isHuman = (args.agent == "human")
        # save the current Bird
        self.bird = bird
        
        # window padding
        self.pad = self.args.padding
        
        # load and reshape all the environment objects' sprites
        self.bg_img = jpg2numpy(self.args.bg_sprite, (self.args.window_size[0]-self.args.ground_height, self.args.window_size[1]))
        self.floor_img = jpg2numpy(self.args.floor_sprite, (self.args.ground_height, self.args.window_size[1]))
        self.pipe_img = jpg2numpy(self.args.pipe_sprite, (self.args.window_size[0], self.args.pipe_width))
        
        # rotated version of the pipe sprite
        rows, cols = self.pipe_img.shape[0:2]
        self.pipe_img_rot = cv2.warpAffine(self.pipe_img, cv2.getRotationMatrix2D((cols/2,rows/2),180,1), (cols,rows))
        
        # generate 'n_pipes' successive pipes
        self.pipes = []
        n_pipes = self.args.window_size[1]//(self.args.pipe_width + self.args.pipe_dist[1]) + 2
        for k in range(n_pipes):
            self.pipes.append(self.generate_pipe())
        
        # build the RGB-pixel array corresponding to the full environment
        self.build_env()
    
    def build_env(self):
        """
        Build and store the RGB-pixel array 'map' corresponding to the full environment: place the objects (bird and pipes) at the right place in the background image.
        Build and store the occupancy grid 'occ' indicating the presence of obstacles: occ[i,j] = 1 if pixel (i,j) represents an obstacle, 0 otherwise.
        """
        # initialize the environment pixel matrix and the occupancy grid
        map = np.zeros((self.args.window_size[0], self.args.window_size[1], 3), dtype=int)
        occ = np.zeros(map.shape[0:2], dtype=int)

        # add the background image
        map[:self.args.window_size[0]-self.args.ground_height, :, :] = self.bg_img
        # add the floor image
        map[self.args.window_size[0]-self.args.ground_height:, :, :] = self.floor_img
        # the floor is an obstacle
        occ[self.args.window_size[0]-self.args.ground_height:, :] = 1
        
        # add all the current pipes in the window
        for pipe in self.pipes:
            x, height = pipe
            
            # check that the pipe is inside the window
            if (x < self.args.window_size[1]):
                # with of the pipe visible in the window
                visible_width = min(x+self.args.pipe_width, self.args.window_size[1]) - x + min(0,x)
                # x-coordinate of the visible front of the pipe
                x = max(x,0)
                # y-coordinate of the top of the bottom pipe
                y = self.args.window_size[0]-self.args.ground_height
                
                # resize the bottom pipe image to match the visible area
                bottom_pipe_img = cv2.resize(self.pipe_img, dsize=(self.args.pipe_width, height), interpolation=cv2.INTER_CUBIC)
                # add the bottom pipe
                map[y - height:y, x:x + visible_width, :] = bottom_pipe_img[:, :visible_width] 
                # the bottom pipe is an obstacle
                occ[y - height:y, x:x + visible_width] = 1

                # y-coordinate of the bottom of the top pipe
                height_top = self.args.window_size[0] - self.args.ground_height - height - self.args.pipe_dist[1]
                # resize the top pipe image to match the visible area
                top_pipe_img = cv2.resize(self.pipe_img_rot, dsize=(self.args.pipe_width, height_top), interpolation=cv2.INTER_CUBIC)
                # add the top pipe
                map[:height_top, x:x + visible_width, :] = top_pipe_img[:, :visible_width] 
                # the top pipe is an obstacle
                occ[:height_top, x:x + visible_width] = 1
            else:
                break
        
        # pad in black the border of the environment
        self.map = np.zeros((self.args.window_size[0] + 2*self.pad, self.args.window_size[1] + 2*self.pad, 3), dtype=int)
        self.map[self.pad: self.pad + self.args.window_size[0], self.pad: self.pad + self.args.window_size[1], :] = map
        
        # add the bird
        if self.bird is not None:
            rows, cols, _ = self.bird.img.shape
            # find the top-left coordinates of bird image
            x_b, y_b = self.bird.x + self.pad - cols//2, max(self.bird.y + self.pad - rows//2, 0)
            # green-screen filtering to display non-square bird shapes
            display_mask = green_screen(self.bird.img)
            # add the bird
            self.map[y_b:y_b + rows, x_b:x_b + cols, :][display_mask] = self.bird.img[display_mask]
        
        # pad with obstacles the border of the environment
        self.occ = np.ones((self.args.window_size[0] + 2*self.pad, self.args.window_size[1] + 2*self.pad), dtype=int)
        self.occ[self.pad: self.pad + self.args.window_size[0], self.pad: self.pad + self.args.window_size[1]] = occ
            
    def generate_pipe(self):
        """Generate a new pipe with random height.
        
        Return:
            'pipe' (tuple, (x, height)): generated pipe (x = coord of front of pipe ; height = height of bottom pipe)
        
        Remarks:
            If this is the first pipe, the generated pipe is placed at the right border of the window for a human and in the middle of the window for an AI.
            Otherwise, the pipe is placed at 'pipe_dist[0]' horizontal distance from the previous pipe.
        """
        # random height of the new pipe
        height = np.random.randint(self.args.pipe_min_height, self.args.window_size[0]-self.args.ground_height-self.args.pipe_dist[1]-self.args.pipe_min_height)
    
        # place the first pipe
        if len(self.pipes) == 0:
            # for a human: after the right border of the window
            if self.isHuman:
                pipe = [self.args.window_size[1], height]
            # for an AI: in the middle of the window
            else:
                pipe = [self.args.window_size[1], height]
        
        # place the new pipe at 'pipe_dist[0]' horizontal distance from the previous one
        else:
            pipe = [self.pipes[-1][0] + self.args.pipe_dist[0] + self.args.pipe_width, height]
        
        return pipe
    
    def get_state(self):
        """Return the state of the Bird.
        The state of the bird is composed of:
            - 'y': the y-coordinate of the Bird center ;
            - 'dx': the x-distance between the Bird and the end of the next pipe's opening ; 
            - 'dy': the y-distance between the Bird and the end of the next pipe's opening. 

        OLD:
            - 'd': the distance between the Bird Center and center of the next pipe's opening ;
            - 'theta': the angle between the Bird Center and center of the next pipe's opening.
            
        Return:
            'state' (np.array, [y, dx, dy]): the state of the Bird)
            
        Remarks:
            The next pipe is the first pipe the bird has not crossed.
        """
        if self.bird is None:
            return None
            
        # current state
        x = self.bird.x
        y = self.bird.y
            
        # coordinates of the center of the next pipe's opening
        next_pipe = list(filter(lambda pipe: pipe[0] + self.args.pipe_width >= self.bird.x - self.args.bird_dims[1], self.pipes))[0]
        x_c = next_pipe[0] + self.args.pipe_width
        y_c = -next_pipe[1] + self.args.window_size[0] - self.args.ground_height - self.args.pipe_dist[1]//2
        
        # OLD version
        #d = np.sqrt((x_c - self.bird.x)**2 + (y_c - self.bird.y)**2)
        #theta = np.arctan2(y_c - self.bird.y, x_c - self.bird.x)
        #state = np.array([y, d, theta])

        dx = x_c - x
        dy = y_c - y
        state = np.array([y, dx, dy])
        
        return state
    
    def scroll(self):
        """Scroll the environment of 1 pixel to the left.
        Update the environment accordingly.
        """
        # number of current pipes to keep
        n_pipes = len(self.pipes)
        
        # move the pipes 1 pixel to the left
        self.pipes = [[pipe[0]-1, pipe[1]] for pipe in self.pipes]
        # remove the pipes that completely left the screen
        self.pipes = list(filter(lambda pipe: pipe[0]+self.args.pipe_width >= 0, self.pipes))
        
        # add new pipes to compensate for removed pipes
        while len(self.pipes) < n_pipes:
            self.pipes.append(self.generate_pipe())
        
        # rebuild the environment
        self.build_env()
        
    
if __name__ == '__main__':
    """Test the scrolling of the environment."""
    # get arguments needed to play the Game
    args = get_game_args()
    environment = Environment(args)

    # get useful handles
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    im = ax.imshow(environment.map)
    # to hide tick values on X and Y axis
    plt.xticks([]), plt.yticks([]) 
    
    # plt event
    def on_click(event):
        # number of frames
        T = 1000

        for t in range(T):
            print("Frame:", t)
            # safe way to pause a plt animation
            plt.pause(0.01)
            # scroll 1 frame and generate the new environment
            environment.scroll()
            # change the displayed image to account for changes
            im.set_data(environment.map)
            # update the image without pausing
            plt.draw()

    # right click to start scrolling
    cid = fig.canvas.mpl_connect('button_press_event', on_click)
    
    plt.show()
    
    # save the current environment to a JPG image
    #cv2.imwrite('test.jpg', environment.map)


    
    
 

