import numpy as np
import matplotlib.pyplot as plt
import cv2

from util import *


class Environment:
    '''
    bg_img: pixel matrix of backgroung (resize to default dimension of bg)
    pipe_img: pixel matrix of pipe (resize to default dimension of pipe)
    pipes: list of 5 elements (x = coord of front of pipes ; height = height of bottom pipe)
        y is randomly generated for new pipe when first pipe leave the screen
    
    
    '''

    def __init__(self, isHuman=True, bird=None):
        super(Environment).__init__()
        
        self.params = game_parameters()
        
        self.isHuman = isHuman
        self.bird = bird
        
        # window padding
        self.pad = self.params["padding"]
        
        # load and reshape all the sprites
        self.bg_img = jpg2numpy(self.params["bg_sprite"], (self.params["window_size"][0]-self.params["ground_height"], self.params["window_size"][1]))
        self.floor_img = jpg2numpy(self.params["floor_sprite"], (self.params["ground_height"], self.params["window_size"][1]))
        self.pipe_img = jpg2numpy(self.params["pipe_sprite"], (self.params["window_size"][0], self.params["pipe_width"]))
        
        # rotated version of the pipe
        rows, cols = self.pipe_img.shape[0:2]
        self.pipe_img_rot = cv2.warpAffine(self.pipe_img, cv2.getRotationMatrix2D((cols/2,rows/2),180,1), (cols,rows))
        
        self.pipes = []
        n_pipes = self.params["window_size"][1]//(self.params["pipe_width"] + self.params["pipe_dist"][1]) + 2
        for k in range(n_pipes):
            self.pipes.append(self.generate_pipe())
                
        self.build_env()
    
    def build_env(self):
        map = np.zeros((self.params["window_size"][0], self.params["window_size"][1], 3), dtype=int)
        occ = np.zeros(map.shape[0:2], dtype=int)

        map[:self.params["window_size"][0]-self.params["ground_height"], :, :] = self.bg_img
        
        map[self.params["window_size"][0]-self.params["ground_height"]:, :, :] = self.floor_img
        occ[self.params["window_size"][0]-self.params["ground_height"]:, :] = 1
        
        for pipe in self.pipes:
            x, height = pipe

            if (x < self.params["window_size"][1]):
                y = self.params["window_size"][0]-self.params["ground_height"]
                visible_width = min(x+self.params["pipe_width"], self.params["window_size"][1]) - x + min(0,x)
                x = max(x,0)
                
                bottom_pipe_img = cv2.resize(self.pipe_img, dsize=(self.params["pipe_width"], height), interpolation=cv2.INTER_CUBIC)
                map[y - height:y, x:x + visible_width, :] = bottom_pipe_img[:, :visible_width] 
                occ[y - height:y, x:x + visible_width] = 1

                
                height_top = self.params["window_size"][0] - self.params["ground_height"] - height - self.params["pipe_dist"][1]
                top_pipe_img = cv2.resize(self.pipe_img_rot, dsize=(self.params["pipe_width"], height_top), interpolation=cv2.INTER_CUBIC)
                map[:height_top, x:x + visible_width, :] = top_pipe_img[:, :visible_width] 
                occ[:height_top, x:x + visible_width] = 1
            else:
                break
        
        self.map = np.zeros((self.params["window_size"][0] + 2*self.pad, self.params["window_size"][1] + 2*self.pad, 3), dtype=int)
        self.map[self.pad: self.pad + self.params["window_size"][0], self.pad: self.pad + self.params["window_size"][1], :] = map
        
        if self.bird is not None:
            rows, cols, _ = self.bird.img.shape
            x_b, y_b = self.bird.x + self.pad - cols//2, max(self.bird.y + self.pad - rows//2, 0)
            display_mask = (self.bird.img[:,:,1] < 100) | (self.bird.img[:,:,0] > self.bird.img[:,:,1]) | (self.bird.img[:,:,2] > self.bird.img[:,:,1]) 
            self.map[y_b:y_b + rows, x_b:x_b + cols, :][display_mask] = self.bird.img[display_mask]
        
        self.occ = np.ones((self.params["window_size"][0] + 2*self.pad, self.params["window_size"][1] + 2*self.pad), dtype=int)
        self.occ[self.pad: self.pad + self.params["window_size"][0], self.pad: self.pad + self.params["window_size"][1]] = occ
            
    def generate_pipe(self):
        height = np.random.randint(self.params["pipe_min_height"], self.params["window_size"][0]-self.params["ground_height"]-self.params["pipe_dist"][1]-self.params["pipe_min_height"])
    
        if len(self.pipes) == 0:
            if self.isHuman:
                pipe = [self.params["window_size"][1], height]
            else:
                pipe = [self.params["window_size"][1]//2, height]

        else:
            pipe = [self.pipes[-1][0] + self.params["pipe_dist"][0] + self.params["pipe_width"], height]
        
        return pipe
        
    def scroll(self):
        n_pipes = len(self.pipes)
        
        self.pipes = [[pipe[0]-1, pipe[1]] for pipe in self.pipes]
        self.pipes = list(filter(lambda pipe: pipe[0]+self.params["pipe_width"] >= 0, self.pipes))
        
        while len(self.pipes) < n_pipes:
            self.pipes.append(self.generate_pipe())
            
        self.build_env()
        
    
if __name__ == '__main__':
    # Test the scrolling of the environment
    environment = Environment()

    # get useful handles
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    im = ax.imshow(environment.map)
    # to hide tick values on X and Y axis
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    
    # plt event
    def on_click(event):
        # number of frames
        T = 10000

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


    
    
 

