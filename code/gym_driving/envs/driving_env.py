from gym_driving.envs.environment import *
from gym_driving.assets.car import *
from gym_driving.assets.terrain import *

import logging
import gym
from gym import spaces
from gym.utils import seeding
import numpy as np
import json
import os

logger = logging.getLogger(__name__)

class DrivingEnv(gym.Env):
    """
    Wrapper class for driving simulator that
    implements the OpenAI Gym interface.
    """
    
    def __init__(self, task, eligible_list=None, render_mode=True, screen=None, config_filepath=None, ran_cen_list=None):
        """
        Initializes driving environment interface, 
        passes most arguments down to underlying environment.

        Args:
            render_mode: boolean, whether to render.
            screen: PyGame screen object, used for rendering.
                Creates own screen object if existing one is not passed in.
            config_filepath: str, path to configuration file.
        """
        
        if config_filepath is None:
            base_dir = os.path.dirname(__file__)

            if task == 'T1':
                config_filepath = os.path.join(base_dir, 'configs/config_task_1.json')
            else:
                config_filepath = os.path.join(base_dir, 'configs/config_task_2.json')

        param_dict = json.load(open(config_filepath, 'r'))
        self.screen_size = param_dict['screen_size']
        self.time_horizon = param_dict['time_horizon']

        if task == 'T2':
            param_dict['terrain_params'] = [
            [
                0, 
                0, 
                4000, 
                4000, 
                "ice"
            ],
            [
                ran_cen_list[0][0], 
                ran_cen_list[0][1], 
                100, 
                100, 
                "dirt"
            ],
    	    [
                ran_cen_list[1][0], 
                ran_cen_list[1][1], 
                100, 
                100, 
                "dirt"
            ],
            [
                ran_cen_list[2][0], 
                ran_cen_list[2][1], 
                100, 
                100, 
                "dirt"
            ],
            [
                ran_cen_list[3][0], 
                ran_cen_list[3][1], 
                100, 
                100, 
                "dirt"
            ],
            [
                0, 
                0, 
                700, 
                700, 
                "icegrass"
            ],
            [
                850, 
                0, 
                1000, 
                150, 
                "road"
            ]
        ]

        self.terrain_params = param_dict['terrain_params']
        self.param_dict = param_dict
        self.screen = screen

        # Default options for PyGame screen, terrain
        if render_mode and screen is None:
            screen = pygame.display.set_mode(self.screen_size)

        if render_mode:
            self.screen = screen
            self.screen.fill((255, 255, 255))

            base_dir = os.path.dirname(os.path.dirname(__file__))
            filename = os.path.join(base_dir, 'assets', 'sprites', 'flag_race.png')
            flag_image = pygame.image.load(filename)
            self.screen.blit(flag_image, (250, 250))

            pygame.display.update()

        self.environment = Environment(task=task, eligible_list=eligible_list, render_mode=render_mode, screen_size=self.screen_size, \
                    screen=self.screen, param_dict=self.param_dict)

        self.render_mode = render_mode
        self.exp_count = self.iter_count = 0

    def _render(self, mode='human', close=False):
        """
        Dummy render command for gym interface.

        Args:
            mode: str
            close: boolean
        """
        pass

    def _step(self, action):
        """
        Updates the environment for one step.

        Args:
            action: 1x2 array, steering / acceleration action.

        Returns:
            state: array, state of environment. 
                Can be positions and angles of cars, or image of environment
                depending on configuration.
            reward: float, reward from action taken.
            done: boolean, whether trajectory is finished.
            info_dict: dict, contains information about environment that may
                not be included in the state.
        """
        
        self.iter_count += 1
        state, reward, terminate, reached_road, info_dict = self.environment.step(action)
        
        if self.iter_count >= self.time_horizon:
            terminate = True
        
        return state, reward, terminate, reached_road, {}
        
    def _reset(self, eligible_list=None):
        """
        Resets the environment.

        Returns:
            state: array, state of environment.
        """
        self.exp_count += 1
        self.iter_count = 0
        self.screen = None

        if self.render_mode:
            self.screen = pygame.display.set_mode(self.screen_size)
            
        state = self.environment.reset(eligible_list, self.screen)
        return state

    