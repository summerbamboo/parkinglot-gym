from gym_driving.assets.car import Car
from gym_driving.assets.terrain import *

import random
import numpy as np
import pygame
import cv2 

class Environment:
    """
    Coordinates updates to participants
    in environment. Interactions should
    be done through simulator wrapper class.
    """
 
    def __init__(self, task, render_mode, screen_size, eligible_list=None, screen=None, param_dict=None):
        """
        Initializes driving environment interface, 
        passes most arguments down to underlying environment.

        Args:
            render_mode: boolean, whether to render.
            screen_size: 1x2 array, 
            screen: PyGame screen object, used for rendering.
                Creates own screen object if existing one is not passed in.
            param_dict: dict, param dictionary containing configuration settings.
        """
        self.task = task
        self.param_dict = param_dict
        self.screen_size = screen_size
        self.screen = screen
        self.render_mode = render_mode
        self.steer_action = self.param_dict['steer_action']
        self.acc_action = self.param_dict['acc_action']
        
        if self.task == 'T1':
            self.reset()
        else:
            self.reset(eligible_list=eligible_list)

    def reset(self, eligible_list=None, screen=None):
        """
        Resets the environment.

        Returns:
            state: array, state of environment.
        """
        if screen is not None:
            self.screen = screen
        
        # Main car starting angle
        low, high, num = self.param_dict['main_car_starting_angles']
        main_car_angle = np.random.choice(np.linspace(low, high, int(num)))

        self.steer_space = [i for i in self.param_dict['steer_action']]
        self.acc_space = [i for i in self.param_dict['acc_action']]

        if self.task == 'T1':
            start_x = random.randint(-300, 300)
            start_y = random.randint(-300, 300)

        else:
            start_x, start_y = random.choice(eligible_list)

        self.main_car = Car(x=start_x, y=start_y, angle=main_car_angle, vel=0, max_vel=13.0, \
            screen=self.screen, screen_size=self.screen_size, texture='main', \
            render_mode=self.render_mode)
       
        self.terrain = []
        for elem in self.param_dict['terrain_params']:   
            self.terrain.append(Terrain(x=elem[0], y=elem[1], width=elem[2], \
                length=elem[3], texture=elem[4], screen=self.screen, screen_size=self.screen_size, \
                render_mode=self.render_mode).create())
                
        self.terrain = sorted(self.terrain, key=lambda x: x.friction)

        self.update_state()
        state, info_dict = self.get_state()
        return state

    def render(self):
        """
        Renders the environment.
        Should only be called if render_mode=True.
        """
        # Clear screen
        self.screen.fill((255, 255, 255))
        screen_coord = (-500.0, -500.0)

        # Update terrain
        for t in self.terrain:
            t.render(screen_coord)

        self.main_car.render(screen_coord)
        
        pygame.display.update()

    def get_state(self):
        """
        Returns current stored state and info dict.

        Returns:
            state: array, state of environment. 
                Can be positions and angles of cars, or image of environment
                depending on configuration.
            info_dict: dict, contains information about environment that may
                not be included in the state.
        """
        return self.state, self.info_dict

    def update_state(self):
        """
        Updates current stored state and info dict.
        """
        info_dict = {}
        main_car_state, info_dict['main_car'] = self.main_car.get_state()
        info_dict['terrain_collisions'] = [terrain for terrain in self.terrain if self.main_car.collide_rect(terrain)]

        # Compact state
        info_dict['compact_state'] = self.get_compact_state()
        state = main_car_state

        self.state, self.info_dict = state, info_dict

    def get_compact_state(self):
        """
        Returns current internal state of the cars in the environment.
        Output state is used to set internal state of environment.

        Returns:
            main_car_info_dict: dict, contains info dict with internal state of main car.
        """
        _, main_car_info_dict = self.main_car.get_state()   

        return main_car_info_dict

    def set_state(self, main_car_state):
        """
        Sets state of all cars in the environment based 
        on input states, obtained by get_compact_state().

        Args:
            main_car_state: dict, contains info dict with internal state of main car.
        """
        self.main_car.set_state(**main_car_state)

    def step(self, action, render_mode=None):
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

        steer = self.steer_space[int(action[0])]
        acc = self.acc_space[int(action[1])]

        if self.task == 'T1':
            steer *= 1.0 + np.random.normal(loc=0.0, scale=0.05)
            acc *= 1.0 + np.random.normal(loc=0.0, scale=0.005)

        else:
            steer *= 1.0 + np.random.normal(loc=0.0, scale=0.5)
            acc *= 1.0 + np.random.normal(loc=0.0, scale=0.5)

        action_unpacked = np.array([steer, acc])

        # Get old state, step
        state, info_dict = self.get_state()
        self.main_car.step(action_unpacked, info_dict)
        self.update_state()

        state, info_dict = self.get_state()
        terrain_collisions = info_dict['terrain_collisions']
        
        done_ice = any([t.texture == 'ice' for t in terrain_collisions])
        done_icegrass = any([t.texture == 'icegrass' for t in terrain_collisions])
        done_road = any([t.texture == 'road' for t in terrain_collisions])
        done_dirt = any([t.texture == 'dirt' for t in terrain_collisions])
        terminate = False
        reached_road = False
        reached_ice = False

        if ((done_ice and not done_icegrass) or done_dirt) and (not done_road):
            reward = -100
            terminate = True
            reached_ice = True

        if done_road:
            reward = 100
            terminate = True
            reached_road = True
        
        else:
            reward = -1

        if render_mode or (render_mode is None and self.render_mode):
            self.render()

        return state, reward, terminate, reached_road, info_dict

