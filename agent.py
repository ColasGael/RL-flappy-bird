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
        self.n_y = 5
        self.n_dx = 10
        self.n_dy = 15

        self.gamma = 0.995
                        
        self.state = state
        
        self.action = 0
        
        self.n_sim = 1
        
        self.eps = 1.
                
        self.t = 0
        
        self.initialize_mdp_data()

    def get_closest_state_idx(self, state, isFail=False):
        y_s, dx_s, dy_s = self.mdp_data["state_discretization"]
        
        i = np.argmin(abs(y_s - state[0]))
        j = np.argmin(abs(dx_s - state[1]))
        k = np.argmin(abs(dy_s - state[2]))
        
        return isFail*self.n_dx*self.n_dy + j*self.n_dy + k
        #return isFail*(j*self.n_dy + k + 1)

    def get_reward(self, hasJumped, isScoreUpdated, isFail):
        
        if isScoreUpdated:
            reward = 100
        elif isFail:
            reward = -1000
        elif hasJumped:
            reward = 0
        else:
            reward = 1  
        
        return reward
    
    def set_transition(self, new_state, hasJumped, isScoreUpdated, isFail):
        reward = self.get_reward(hasJumped, isScoreUpdated, isFail)
        #self.update_Q(reward, new_state, isFail)
        #self.update_theta(reward, new_state)
        self.update_mdp_transition_counts_reward_counts(self.state, self.action, new_state, reward, isFail)

        self.state = new_state
        
        if isFail:
            self.update_mdp_transition_probs_reward()
            self.update_mdp_value(0.01)
            PressString("n")
    
    def reset(self, state):
        self.state = state
        self.n_sim += 1
        self.eps += 0.01
        self.t = 0

        LeftClick()
    
    def jump(self):
            self.t = 0
            PressString(" ")
    
    def choose_action(self):
        if np.random.rand() < self.eps:            
            self.action = self.best_action(self.state)
        else:
            self.action = np.random.rand() < 0.01
            
        if self.action == 1:
            self.jump()
        else:
            self.t += 1
                
    def initialize_mdp_data(self):
        """
        Return a variable that contains all the parameters/state you need for your MDP.
        Feel free to use whatever data type is most convient for you (custom classes, tuples, dicts, etc)
        Assume that no transitions or rewards have been observed.
        Initialize the value function array to small random values (0 to 0.10, say).
        Initialize the transition probabilities uniformly (ie, probability of
            transitioning for state x to state y using action a is exactly
            1/num_states).
        Initialize all state rewards to zero.
        Args:
            num_states: The number of states
        Returns: The initial MDP parameters
        """
        
        # state discretization
        y_s = np.linspace(0, self.args.window_size[0]-self.args.ground_height, self.n_y)
        dx_s = np.linspace(0, self.args.pipe_dist[0], self.n_dx)
        dy_s = np.linspace(-(self.args.window_size[0]-self.args.ground_height), self.args.window_size[0]-self.args.ground_height, self.n_dy)
        
        # OLD version of the state
        #self.d_s = np.linspace(0, np.sqrt((self.args.window_size[0]-self.args.ground_height)**2 + self.args.pipe_dist[0]**2), self.n_d)
        #self.theta_s = np.linspace(-np.pi/2, np.pi/2, self.n_theta)
        #num_states = s2*elf.n_d*self.n_theta
        
        num_states = 2*self.n_dx*self.n_dy
        #num_states = self.n_states**2+1

        transition_counts = np.zeros((num_states, num_states, 2))
        transition_probs = np.ones((num_states, num_states, 2)) / num_states
        reward_counts = np.zeros((num_states, 2))
        reward = np.zeros(num_states)
        value = np.zeros(num_states)

        self.mdp_data = {
            'state_discretization': [y_s, dx_s, dy_s],
            'transition_counts': transition_counts,
            'transition_probs': transition_probs,
            'reward_counts': reward_counts,
            'reward': reward,
            'value': value,
            'num_states': num_states,
        }
        # *** END CODE HERE ***

    def best_action(self, state):
        """
        Choose the next action (0 or 1) that is optimal according to your current
        mdp_data. When there is no optimal action, return a random action.
        Args:
            state: The current state in the MDP
            mdp_data: The parameters for your MDP. See initialize_mdp_data.
        Returns:
            0 or 1 that is optimal according to your current MDP
        """

        # *** START CODE HERE ***
        s = self.get_closest_state_idx(state)
        
        score1 = self.mdp_data['transition_probs'][s, :, 0].dot(self.mdp_data['value'])
        score2 = self.mdp_data['transition_probs'][s, :, 1].dot(self.mdp_data['value'])

        if score1 >= score2:
            action = 0
        elif score2 > score1:
            action = 1

        return action
        # *** END CODE HERE ***

    def update_mdp_transition_counts_reward_counts(self, state, action, new_state, reward, isFail):
        """
        Update the transition count and reward count information in your mdp_data. 
        Do not change the other MDP parameters (those get changed later).
        Record the number of times `state, action, new_state` occurs.
        Record the rewards for every `new_state`.
        Record the number of time `new_state` was reached.
        Args:
            mdp_data: The parameters of your MDP. See initialize_mdp_data.
            state: The state that was observed at the start.
            action: The action you performed.
            new_state: The state after your action.
            reward: The reward after your action.
        Returns:
            Nothing
        """

        # *** START CODE HERE ***
        
        s = self.get_closest_state_idx(state, False)
        new_s = self.get_closest_state_idx(new_state, isFail)

        self.mdp_data['transition_counts'][s, new_s, action] += 1
        self.mdp_data['reward_counts'][s, 0] += reward
        self.mdp_data['reward_counts'][s, 1] += 1

        # *** END CODE HERE ***

        # This function does not return anything
        return

    def update_mdp_transition_probs_reward(self):
        """
        Update the estimated transition probabilities and reward values in your MDP.
        Make sure you account for the case when a state-action pair has never
        been tried before, or the state has never been visited before. In that
        case, you must not change that component (and thus keep it at the
        initialized uniform distribution).
        
        Args:
            mdp_data: The data for your MDP. See initialize_mdp_data.
        Returns:
            Nothing
        """

        # *** START CODE HERE ***
        for a in [0, 1]:
            for s in range(self.mdp_data['num_states']):
                total_num_transitions = np.sum(self.mdp_data['transition_counts'][s, :, a])
                if total_num_transitions > 0:
                    self.mdp_data['transition_probs'][s, :, a] = (
                        self.mdp_data['transition_counts'][s, :, a] / total_num_transitions
                    )

        for s in range(self.mdp_data['num_states']):
            if self.mdp_data['reward_counts'][s, 1] > 0:
                self.mdp_data['reward'][s] = self.mdp_data['reward_counts'][s, 0] / self.mdp_data['reward_counts'][s, 1]

        # *** END CODE HERE ***

        # This function does not return anything

    def update_mdp_value(self, tolerance):
        """
        Update the estimated values in your MDP.
        Perform value iteration using the new estimated model for the MDP.
        The convergence criterion should be based on `TOLERANCE` as described
        at the top of the file.
        Return true if it converges within one iteration.
        
        Args:
            mdp_data: The data for your MDP. See initialize_mdp_data.
            tolerance: The tolerance to use for the convergence criterion.
            gamma: Your discount factor.
        Returns:
            True if the value iteration converged in one iteration
        """

        # *** START CODE HERE ***
        
        iterations = 0

        while True:
            new_value = np.zeros(self.mdp_data['num_states'])

            iterations = iterations + 1
            for s in range(self.mdp_data['num_states']):
                value1 = self.mdp_data['transition_probs'][s, :, 0].dot(self.mdp_data['value'])
                value2 = self.mdp_data['transition_probs'][s, :, 1].dot(self.mdp_data['value'])

                new_value[s] = max(value1, value2)

            new_value = self.mdp_data['reward'] + self.gamma * new_value

            max_diff = float('-Inf')
            for s in range(self.mdp_data['num_states']):
                if abs(new_value[s] - self.mdp_data['value'][s]) > max_diff:
                    max_diff = abs(new_value[s] - self.mdp_data['value'][s])

            self.mdp_data['value'] = new_value

            if max_diff < tolerance:
                break

        return iterations == 1

        # *** END CODE HERE ***                