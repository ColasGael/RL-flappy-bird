import numpy as np

from util import *

class Bird:
    
    def __init__(self):
        self.params = game_parameters()

        self.img = jpg2numpy(self.params["bird_sprite"], self.params["bird_dims"])
        self.x = self.params["bird_pos"][0]
        self.y = self.params["bird_pos"][1]
        
        self.t = int(self.params["dt"] * self.params["v0"] / self.params["a0"])
    
    def jump(self):
        self.t = 0
        
    def move(self):   
        self.t += 1
        
        time = self.t / self.params["dt"]
        
        self.y -= max(time*self.params["v0"] + (self.t <5)*self.params["dv"] -0.5*time**2*self.params["a0"], -self.params["v_max"])
        
        self.y = max(int(self.y), 0)
        

    

