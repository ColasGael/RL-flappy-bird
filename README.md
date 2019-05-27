# RL-flappy-bird
Reinforcement Learning on a playable version of Flappy Bird.

## RL algorithm

The state is composed of: the status (alive or dead) of the Bird as well as its horizontal and vertical distances with the end of the next pipe opening.

The AI agent explores its environment with an increasingly greedy Epsilon-Greedy scheme.

At the end of each simulation, it updates its approximation of the underlying Markov Decision Process. The state space is descretized.
Then it solves for the optimal value function via Value Iteration.

The best action in a given state is the one that yields the largest value function in this state.

## How to play?

This game is also playable by humans. 
To play it, go at the root of the repository and run: `python game.py`

A window will open. The scores and the commands are displayed on the right side of the window.

## How to let the AI play?

To let the AI agent learn, go at the root of the repository and run: `python game.py --agent ai`

If you want to load a pretrained agent, add the following flag: `python game.py --agent ai --load_save True`

You can also save your own agent's state by pressing "Z" during the simulation.

## How to customize?

The sprites (for the bird, the pipes and the background) used in the games are customizable. If you want to use your own:
- put the new sprite as JPG files in the "sprites" directory ;
- update the "args.py" with the new sprites filenames.

You can also modify "args.py" to change the parameters of the simulation:
    - the dimensions of the environment;
    - the dynamics of the bird movements;
    - the Reinforcement Learning hyperparameters.

## Requirements

To install all the necessary packages, go at the root of the repository and run: `pip install -r requirements`
