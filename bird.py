import numpy as np
import cv2

# dynamics parameters
V = 0.4
A = 0.3
DT = 10
V_MAX = 3
DV = 2
# bird dimensions
BIRD_DIMS = (20, 20)

# Sprites used
BIRD_SPRITE = "sprites/bird_rocket.jpg"

class Bird:
    
    def __init__(self):
        self.img = np.flip(cv2.resize(cv2.imread(BIRD_SPRITE), dsize=(BIRD_DIMS[1], BIRD_DIMS[0]), interpolation=cv2.INTER_CUBIC), axis=-1)
        np.save("test", self.img)
        self.x = -1
        self.y = 150
        self.t = int(DT*V/A)
    
    def jump(self):
        self.t = 0
        
    def move(self):   
        self.t += 1
        
        time = self.t/DT
        
        self.y -= max(time*V -0.5*time**2*A + (self.t <5)*DV, -V_MAX)
        
        self.y = max(int(self.y), 0)
        

    

