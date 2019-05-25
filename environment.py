import numpy as np
import matplotlib.pyplot as plt
import cv2
import time

# Environment characteristics
WINDOW_SIZE = (370, 240) 
GROUND_HEIGHT = 64
PIPE_WIDTH = 40
PIPE_V_DIST = 80
PIPE_H_DIST = 90
MIN_PIPE_HEIGHT = 10
BIRD_X = 80
PADDING = 5

# Sprites used
BG_SPRITE = "sprites/bg_fb.jpg"
FLOOR_SPRITE = "sprites/floor_fb.jpg"
PIPE_SPRITE = "sprites/pipe_fb.jpg"

class Environment:
    '''
    bg_img: pixel matrix of backgroung (resize to default dimension of bg)
    pipe_img: pixel matrix of pipe (resize to default dimension of pipe)
    pipes: list of 5 elements (x = coord of front of pipes ; height = height of bottom pipe)
        y is randomly generated for new pipe when first pipe leave the screen
    
    
    '''

    def __init__(self, isHuman=True, bird=None):
        super(Environment).__init__()
        self.isHuman = isHuman
        self.bird = bird
        
        if bird is not None:
            self.bird.x = BIRD_X
        
        # load and reshape all the sprites
        self.bg_img = np.flip(cv2.resize(cv2.imread(BG_SPRITE), dsize=(WINDOW_SIZE[1], WINDOW_SIZE[0]-GROUND_HEIGHT), interpolation=cv2.INTER_CUBIC), axis=-1)
        self.floor_img = np.flip(cv2.resize(cv2.imread(FLOOR_SPRITE), dsize=(WINDOW_SIZE[1], GROUND_HEIGHT), interpolation=cv2.INTER_CUBIC), axis=-1)
        self.pipe_img = np.flip(cv2.resize(cv2.imread(PIPE_SPRITE), dsize=(PIPE_WIDTH, WINDOW_SIZE[0]), interpolation=cv2.INTER_CUBIC), axis=-1)
        
        # rotated version of the pipe
        rows, cols = self.pipe_img.shape[0:2]
        self.pipe_img_rot = cv2.warpAffine(self.pipe_img, cv2.getRotationMatrix2D((cols/2,rows/2),180,1), (cols,rows))
        
        self.pipes = []
        n_pipes = WINDOW_SIZE[1]//(PIPE_WIDTH + PIPE_H_DIST) + 2
        for k in range(n_pipes):
            self.pipes.append(self.generate_pipe())
        
        self.pad = PADDING
        
        self.build_env()
    
    def build_env(self):
        map = np.zeros((WINDOW_SIZE[0], WINDOW_SIZE[1], 3), dtype=int)
        occ = np.zeros((WINDOW_SIZE[0], WINDOW_SIZE[1]), dtype=int)

        map[:WINDOW_SIZE[0]-GROUND_HEIGHT, :, :] = self.bg_img
        
        map[WINDOW_SIZE[0]-GROUND_HEIGHT:, :, :] = self.floor_img
        occ[WINDOW_SIZE[0]-GROUND_HEIGHT:, :] = 1
        
        for pipe in self.pipes:
            x, height = pipe

            if (x < WINDOW_SIZE[1]):
                y = WINDOW_SIZE[0]-GROUND_HEIGHT
                visible_width = min(x+PIPE_WIDTH, WINDOW_SIZE[1]) - x + min(0,x)
                x = max(x,0)
                
                bottom_pipe_img = cv2.resize(self.pipe_img, dsize=(PIPE_WIDTH, height), interpolation=cv2.INTER_CUBIC)
                map[y - height:y, x:x + visible_width, :] = bottom_pipe_img[:, :visible_width] 
                occ[y - height:y, x:x + visible_width] = 1

                
                height_top = WINDOW_SIZE[0] - GROUND_HEIGHT - height - PIPE_V_DIST
                top_pipe_img = cv2.resize(self.pipe_img_rot, dsize=(PIPE_WIDTH, height_top), interpolation=cv2.INTER_CUBIC)
                map[:height_top, x:x + visible_width, :] = top_pipe_img[:, :visible_width] 
                occ[:height_top, x:x + visible_width] = 1
            else:
                break
        
        self.map = np.zeros((WINDOW_SIZE[0] + 2*self.pad, WINDOW_SIZE[1] + 2*self.pad, 3), dtype=int)
        self.map[self.pad: self.pad + WINDOW_SIZE[0], self.pad: self.pad + WINDOW_SIZE[1], :] = map
        
        if self.bird is not None:
            rows, cols, _ = self.bird.img.shape
            x_b, y_b = self.bird.x + self.pad - cols//2, max(self.bird.y + self.pad - rows//2, 0)
            display_mask = (self.bird.img[:,:,0] != 0) | (self.bird.img[:,:,1] != 255) | (self.bird.img[:,:,1] != 0)
            self.map[y_b:y_b + rows, x_b:x_b + cols, :][display_mask] = self.bird.img[display_mask]
        
        self.occ = np.ones((WINDOW_SIZE[0] + 2*self.pad, WINDOW_SIZE[1] + 2*self.pad), dtype=int)
        self.occ[self.pad: self.pad + WINDOW_SIZE[0], self.pad: self.pad + WINDOW_SIZE[1]] = occ
            
    def generate_pipe(self):
        height = np.random.randint(MIN_PIPE_HEIGHT, WINDOW_SIZE[0]-GROUND_HEIGHT-PIPE_V_DIST-MIN_PIPE_HEIGHT)
    
        if len(self.pipes) == 0:
            if self.isHuman:
                pipe = [WINDOW_SIZE[1], height]
            else:
                pipe = [WINDOW_SIZE[1]//2, height]

        else:
            pipe = [self.pipes[-1][0] + PIPE_H_DIST + PIPE_WIDTH, height]
        
        return pipe
        
    def scroll(self):
        n_pipes = len(self.pipes)
        
        self.pipes = [[pipe[0]-1, pipe[1]] for pipe in self.pipes]
        self.pipes = list(filter(lambda pipe: pipe[0]+PIPE_WIDTH >= 0, self.pipes))
        
        while len(self.pipes) < n_pipes:
            self.pipes.append(self.generate_pipe())
            
        self.build_env()
        
    
if __name__ == '__main__':
    environment = Environment()

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    im = ax.imshow(environment.map)
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    
    def on_click(event):
        T = 10000

        for t in range(T):
            print("Frame:", t)
            plt.pause(0.01)
            environment.scroll()
            im.set_data(environment.map)
            plt.draw()


    cid = fig.canvas.mpl_connect('button_press_event', on_click)
    
    plt.show()
    
    #cv2.imwrite('test.jpg', environment.map)


    
    
 

