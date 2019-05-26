"""Command-line arguments for the Game.

Authors:
    Gael Colas
"""

import argparse


def get_game_args():
    """Get arguments needed to play the Game."""
    
    parser = argparse.ArgumentParser('Get arguments needed to play the Game.')
    
    # add arguments needed to build the environment
    add_env_args(parser)
    # add arguments needed to describe the bird dynamics
    add_dynamics_args(parser)
    # add arguments needed to display the environment
    add_sprites_args(parser)
    
    parser.add_argument('--commands_filename',
                        type=str,
                        default="commands.txt",
                        help="Filename of the text file listing the commands used in the game.")
    
    parser.add_argument('--agent',
                        type=str,
                        default="human",
                        choices=("human", "ai"),
                        help="Whether to use a human or an AI agent.")
    
    args = parser.parse_args()

    return args


def add_sprites_args(parser):
    """Add arguments (sprites) needed to display the environment."""
    parser.add_argument('--bg_sprite',
                        type=str,
                        default="sprites/bg_fb.jpg",
                        help="Sprite filename for the background.")
    parser.add_argument('--floor_sprite',
                        type=str,
                        default="sprites/floor_fb.jpg",
                        help="Sprite filename for the bottom floor.")
    parser.add_argument('--pipe_sprite',
                        type=str,
                        default="sprites/pipe_fb.jpg",
                        help="Sprite filename for the pipes.")
    parser.add_argument('--bird_sprite',
                        type=str,
                        default="sprites/bird_rocket.jpg",
                        help="Sprite filename for the bird.")
    parser.add_argument('--explosion_sprite',
                        type=str,
                        default="sprites/explosion.jpg",
                        help="Sprite filename for the explosion.")    

                        
def add_dynamics_args(parser):
    """Add arguments needed to describe the bird dynamics."""
    parser.add_argument('--v0',
                        type=float,
                        default=0.04,
                        help="Initial velocity at the jump.")
    parser.add_argument('--a0',
                        type=float,
                        default=0.003,
                        help="Negative acceleration (gravity) felt by the bird.")
    parser.add_argument('--v_max',
                        type=float,
                        default=3,
                        help="Maximum velocity (pixel decrease per time step) of the bird in descent.")
    parser.add_argument('--dy',
                        type=float,
                        default=2.,
                        help="Initial vertical velocity boost (pixel increase per time step) in the first time steps of the jump.")


def add_env_args(parser):
    """Add arguments needed to build the environment."""
    # Objects' dimensions in pixels
        # window
    parser.add_argument('--window_size',
                        type=tuple,
                        default=(370, 240),
                        help="Dimensions (H, W) of the game window in pixels.")
    parser.add_argument('--padding',
                        type=int,
                        default=5,
                        help="Border width of the game window in pixels.")
        # environment
    parser.add_argument('--ground_height',
                        type=int,
                        default=64,
                        help="Height of the bottom ground in pixels.")
    parser.add_argument('--pipe_width',
                        type=int,
                        default=40,
                        help="Width of a pipe in pixels.")
    parser.add_argument('--pipe_min_height',
                        type=int,
                        default=20, #10,
                        help="Minimum height of a pipe in pixels.")
    parser.add_argument('--pipe_dist',
                        type=tuple,
                        default=(90, 80),
                        help="Distance between pipes (horizontal, vertical) in pixels.")
        # bird
    parser.add_argument('--bird_dims',
                        type=tuple,
                        default=(20, 20),
                        help="Dimensions (H, W) of the bird in pixels.") 
    parser.add_argument('--bird_pos',
                        type=tuple,
                        default=(80, 150),
                        help="Initial position (x, y) of the bird in pixels.") 
        # explosion
    parser.add_argument('--explosion_dims',
                        type=tuple,
                        default=(50, 50),
                        help="Dimensions (H, W) of the explosion in pixels.") 
