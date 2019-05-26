# RL-flappy-bird
Reinforcement Learning on a playable version of Flappy Bird.

## How to play?

This game is also playable by humans. 
To play it, go at the root of the repository and run: `python game.py`

A window will open. The commands are displayed on the right side of the window.

## How to customize?

The sprites (for the bird, the pipes and the background) used in the games are customizable. If you want to use your own:
- put the new sprite as JPG files in the "sprites" directory ;
- update the "args.py" with the new sprites filenames.

You can also modify "args.py" to change some parameters of the simulation (dimensions of the environment, dynamics of the bird movements, ...).

## Requirements

To install all the necessary packages, go at the root of the repository and run: `pip install -r requirements`
