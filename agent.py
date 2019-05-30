"""AI agent using RL to beat the game.

Authors:
    Gael Colas
    Sanyam Mehra (CS229 teaching staff): HW4 solutions
"""

import numpy as np

from keyboard_event_generator import PressString, LeftClick


class AIAgent:
    """AI agent controlling the bird.
    The AI agent is trained by Reinforcement Learning.
    Every time the agent finishes a simulation, he builds an approximate Markov Decision Process based on the transition and the reward observed.
    At the end of the simulation, he computes the approximated value function through Value Iteration.
    This value function is then used to choose the best actions of the next simulation.
    
    Attributes:
        'args' (ArgumentParser): parser gethering all the Game parameters
        'n_states' (tuple of int, (n_y, n_dx, n_dy)): discretization = number of points in each axis of the state
        'gamma' (float): discount factor
        'eps' (float): epsilon-greedy coefficient
        'mdp' (MDP): approximate MDP current parameters
        'n_sim' (int): number of simulations
        
        'state' (np.array, [y, dx, dy]): the current state of the Bird
        'action' (int): the current action 
                action = 1 if jumping, 0 otherwise
    """
    
    def __init__(self, args, state):
        super(AIAgent).__init__()
        
        # RL parameters
        self.args = args
        self.n_states = args.n_states
        self.gamma = args.gamma
        self.eps = 1.
        self.tolerance = args.tolerance
        # initialize the approximate MDP parameters
        self.initialize_mdp_data()
        # current simulation
        self.n_sim = 1
        
        # current state and action
        self.state = state
        self.action = 0

    def get_reward(self, isScoreUpdated, isFail):
        """Reward function.
        
        Args:
            'isScoreUpdated' (bool): whether the agent has earned a point at the current state
            'isFail' (bool): whether the Game has been failed at the current state
            
        Return:
            'reward' (float): reward earned in the current state
            
        Remarks:
            Earning a point: +100
            Losing the game: -1000
            Being alive: +1
        """
        if isScoreUpdated:
            reward = 100
        elif isFail:
            reward = -1000
        else:
            reward = 1  
        
        return reward
    
    def choose_action(self):
        """Choose the next action with an Epsilon-Greedy exploration strategy.
        """
        def jump():
            """Execute the jumping action.
            """
            PressString(" ")
        
        if np.random.rand() < self.eps:            
            self.action = self.best_action(self.state)
        else:
            self.action = np.random.rand() < 0.01
            
        if self.action == 1:
            jump()
    
    def reset(self, state):
        """Reset the simulation parameters.
        """
        self.n_sim += 1

        # initial state and action
        self.state = state
        
        # make the algorithm more greedy
        self.eps += 0.01
        
        # start a new simulation
        LeftClick()
    
    def set_transition(self, new_state, isScoreUpdated, isFail):
        """Update the approximate MDP with the given transition.
        
        Args:
            'new_state' (np.array, [y, dx, dy]): the new state of the Bird
            'isScoreUpdated' (bool): whether the agent has earned a point at the last state
            'isFail' (bool): whether the Game has been failed at the last state
        """
        # get the previous state reward
        reward = self.get_reward(isScoreUpdated, isFail)
        # store the given transition
        self.update_mdp_counts(self.state, self.action, new_state, reward, isFail)
        
        # update the current state
        self.state = new_state
        
        # end of the current simulation 
        if isFail:
            # update the approximate MDP with the simulation observations
            self.update_mdp_parameters()
            # start a new simulation
            PressString("n")
    
    def get_closest_state_idx(self, state, isFail=False):
        """Get the index of the closest discretized state.
        
        Args:
            'state' (np.array, [y, dx, dy]): the current state of the Bird
            'isFail' (bool): whether the Game is failed
            
        Return:
            'ind' (int): index of the closes discretized state
            
        Remarks:
            State 0 is a FAIL state.
        """
        # discretized state
        y_s, dx_s, dy_s = self.mdp_data["state_discretization"]
        
        # closest discretized state indices
        i = np.argmin(abs(y_s - state[0]))
        j = np.argmin(abs(dx_s - state[1]))
        k = np.argmin(abs(dy_s - state[2]))
        
        return (not isFail)*(j*self.n_states[2] + k + 1)

    def initialize_mdp_data(self):
        """Save a attributes 'mdp_data' that contains all the parameters defining the approximate MDP.
        
        Parameters:
            'num_states' (int): the number of discretized states.
                    num_states = n_dx*n_dy + 1
        
        Initialization scheme:
            - Value function array initialized to 0
            - Transition probability initialized uniformly: p(x'|x,a) = 1/num_states 
            - State rewards initialized to 0
        """
        
        # state discretization
        num_states = self.n_states[1]*self.n_states[2] + 1
        y_s = np.linspace(0, self.args.window_size[0]-self.args.ground_height, self.n_states[0])
        dx_s = np.linspace(0, self.args.pipe_dist[0], self.n_states[1])
        dy_s = np.linspace(-(self.args.window_size[0]-self.args.ground_height), self.args.window_size[0]-self.args.ground_height, self.n_states[2])
        
        # OLD version of the state
        #self.d_s = np.linspace(0, np.sqrt((self.args.window_size[0]-self.args.ground_height)**2 + self.args.pipe_dist[0]**2), self.n_d)
        #self.theta_s = np.linspace(-np.pi/2, np.pi/2, self.n_theta)
        #num_states = s2*elf.n_d*self.n_theta

        transition_counts = np.zeros((num_states, 2, num_states))
        transition_probs = np.ones((num_states, 2, num_states)) / num_states
        reward_counts = np.zeros((num_states, 2))
        reward = np.zeros(num_states)
        value = np.zeros(num_states)

        self.mdp_data = {
            'num_states': num_states,
            'state_discretization': [y_s, dx_s, dy_s],
            'transition_counts': transition_counts,
            'transition_probs': transition_probs,
            'reward_counts': reward_counts,
            'reward': reward,
            'value': value
        }

    def best_action(self, state):
        """Choose the next action (0 or 1) that is optimal according to your current 'mdp_data'. 
        When there is no optimal action, return 0 has "not jumping" is more frequent.
        
        Args:
            'state' (np.array, [y, dx, dy]): current state of the Bird
            
        Return:
            'action' (int, 0 or 1): optimal action in the current state according to the approximate MDP
        """
        # get the index of the closest discretized state
        s = self.get_closest_state_idx(state)
        
        # value function if taking each action in the current state 
        score_nojump = self.mdp_data['transition_probs'][s, 0, :].dot(self.mdp_data['value'])
        score_jump = self.mdp_data['transition_probs'][s, 1, :].dot(self.mdp_data['value'])

        # best action in the current state
        action = (score_jump > score_nojump)*1

        return action

    def update_mdp_counts(self, state, action, new_state, reward, isFail):
        """Update the transition counts and reward counts based on the given transition.
        
        Record for all the simulations:
            - the number of times `state, action, new_state` occurs ;
            - the rewards accumulated for every `new_state`.
        
        Args:
            'state' (np.array, [y, dx, dy]): previous state of the Bird
            'action' (int, 0 or 1): last action performed
            'new_state' (np.array, [y, dx, dy]): new state after performing the action in the previous state
            'reward' (float): reward observed in the previous state
        """
        # get the index of the closest discretized previous and new states
        s = self.get_closest_state_idx(state, False)
        new_s = self.get_closest_state_idx(new_state, isFail)

        # update the transition and the reward counts
        self.mdp_data['transition_counts'][s, action, new_s] += 1
        self.mdp_data['reward_counts'][new_s, 0] += reward
        self.mdp_data['reward_counts'][new_s, 1] += 1

    def update_mdp_parameters(self):
        """Update the estimated MDP parameters (transition and reward functions) at the end of a simulation.
        Perform value iteration using the new estimated model for the MDP.

        Remarks:
            Only observed transitions are updated.
            Only states with observed rewards are updated.
        """
        temp = self.mdp_data['transition_probs'].copy()
        # update the transition function
        total_num_transitions = np.sum(self.mdp_data['transition_counts'], axis=-1)
        visited_state_action_pairs = total_num_transitions > 0
        self.mdp_data['transition_probs'][visited_state_action_pairs] = self.mdp_data['transition_counts'][visited_state_action_pairs] / total_num_transitions[visited_state_action_pairs, np.newaxis]

        # update the reward function
        visited_states = self.mdp_data['reward_counts'][:, 1] > 0
        self.mdp_data['reward'][visited_states] = self.mdp_data['reward_counts'][visited_states, 0] / self.mdp_data['reward_counts'][visited_states, 1]

        # update the value function through Value Iteration
        while True:           
            # Q(_,a) for the different actions
            value_nojump = np.dot(self.mdp_data['transition_probs'][:,0,:], self.mdp_data['value'])
            value_jump = np.dot(self.mdp_data['transition_probs'][:,1,:], self.mdp_data['value'])

            # Bellman update
            new_value = self.mdp_data['reward'] + self.gamma * np.maximum(value_nojump, value_jump)
            
            # difference with previous value function
            max_diff = np.max(np.abs(new_value - self.mdp_data['value']))

            self.mdp_data['value'] = new_value
            
            # check for convergence
            if max_diff < self.tolerance:
                break
