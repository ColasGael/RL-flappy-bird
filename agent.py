"""AI agent using RL to beat the game.

Authors:
    Gael Colas
"""

import numpy as np

from keyboard_event_generator import PressString, LeftClick


class AIAgent:
    
    def __init__(self, args, state):
        super(AIAgent).__init__()
        
        self.args = args
        self.n_states = 20
        
        self.gamma = 0.95
        
        self.alpha = 0.01
        
        self.create_state_dict()
        
        self.state = state
        
        self.last_action = False
        
        self.n_sim = 1
        
        self.eps = 1.
        
        self.theta = np.zeros((4, 2))
        
        self.t = 0
        
    def beta(self, state):
        return np.reshape(np.concatenate(([1], state)), (1,-1))
        
    def create_state_dict(self):
        self.y_s = np.linspace(0, self.args.window_size[0]-self.args.ground_height, self.n_states)
        self.d_s = np.linspace(0, np.sqrt((self.args.window_size[0]-self.args.ground_height)**2 + self.args.pipe_dist[0]**2), self.n_states)
        self.theta_s = np.linspace(0, 2*np.pi, self.n_states)
        
        #self.Q = {(y, d, theta): np.array([0., 0.]) for y in self.y_s for d in self.d_s for theta in self.theta_s}
        self.Q = {(d, theta): np.array([0., -1.]) for y in self.y_s for d in self.d_s for theta in self.theta_s}

    def get_closest_state(self, state):
        i = np.argmin(abs(self.y_s - state[0]))
        j = np.argmin(abs(self.d_s - state[1]))
        k = np.argmin(abs(self.theta_s - state[2]))
        
        #return (self.y_s[i], self.d_s[j], self.theta_s[k])
        return (self.d_s[j], self.theta_s[k])

    def update_theta(self, reward, new_state):
        
        if self.last_action:
            self.theta[:,1] = self.theta[:,1] + self.alpha*(reward + self.gamma*np.max(np.dot(self.beta(new_state), self.theta)) - np.dot(self.theta[:,1], np.squeeze(self.beta(self.state))))*self.beta(self.state)
        else:
            self.theta[:,0] = self.theta[:,0] + self.alpha*(reward + self.gamma*np.max(np.dot(self.beta(new_state), self.theta)) - np.dot(self.theta[:,0], np.squeeze(self.beta(self.state))))*self.beta(self.state)
    
    def update_Q(self, reward, new_state):
        current_state = self.get_closest_state(self.state)
        next_state = self.get_closest_state(new_state)
        
        if self.last_action:
            self.Q[current_state][1] = self.Q[current_state][1] + self.alpha*(reward + self.gamma*np.max(self.Q[next_state]) - self.Q[current_state][1])
        else:
            self.Q[current_state][0] = self.Q[current_state][0] + self.alpha*(reward + self.gamma*np.max(self.Q[next_state]) - self.Q[current_state][0])
    
    def get_reward(self, isScoreUpdated, isFail):
        
        if isScoreUpdated:
            reward = 100
        elif isFail:
            reward = -1000
            print(self.t)
        else:
            reward = 1  
        
        return reward
    
    def set_state(self, new_state, isScoreUpdated, isFail):
        reward = self.get_reward(isScoreUpdated, isFail)
        self.update_Q(reward, new_state)
        #self.update_theta(reward, new_state)
        self.state = new_state
        
        if isFail:
            PressString("n")
    
    def reset(self, state):
        self.state = state
        self.t = 0
        self.n_sim += 1
        self.eps += 0.01
        print(self.n_sim, self.eps)
        
        LeftClick()
    
    def action(self):
        if np.random.rand() < self.eps:
            current_state = self.get_closest_state(self.state)
            
            isJump = np.argmax(self.Q[current_state]) == 1
            #isJump = np.argmax(np.dot(self.beta(self.state), self.theta)) == 1
            
            self.last_action = (self.last_action and self.t < 50) or isJump
            
            if isJump:
                self.t = 0
                PressString(" ")
            else:
                self.t += 1
                
        else:
            isJump = np.random.rand() < 0.01
            self.last_action = (self.last_action and self.t < 50 ) or isJump

            if isJump:
                self.t = 0
                PressString(" ")
            else: 
                self.t += 1  
