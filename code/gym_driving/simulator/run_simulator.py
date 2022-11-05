from importlib.resources import path
from gym_driving.assets.car import *
from gym_driving.envs.environment import *
from gym_driving.envs.driving_env import *
from gym_driving.assets.terrain import *

import time
import pygame, sys
from pygame.locals import *
import random
import math
import argparse

# Do NOT change these values
TIMESTEPS = 1000
FPS = 30
NUM_EPISODES = 10

class Task1():

    def __init__(self):
        """
        Can modify to include variables as required
        """

        super().__init__()
    
    # chase the point (x0,y0)
    def chase(self, state, x0, y0):
        x, y, _, o = state
        # signed coordinates with respect to center of road as origin
        x1 = x - x0
        y1 = -(y - y0)
        # change orientation to (-180,180]
        if o < 180:
            o1 = -o
        else:
            o1 = 360 - o
        # direction to go
        t = math.atan2(y1,x1) * 180 / math.pi
        # car in upper half
        if t >= 0:
            # car almost aligned
            if o1 <= t - 177 and o1 >= t - 183:
                action_acc = 4
                action_steer = 1
            else:
                # steering required
                action_acc = 2
                # clockwise
                if o1 > t - 177:
                    action_steer = 2
                # anti-clockwise
                elif o1 < t - 183:
                    action_steer = 0
        # car in lower half
        else:
            # car almost aligned
            if o1 >= t + 177 and o1 <= t + 183:
                action_acc = 4
                action_steer = 1
            else:
                # steering required
                action_acc = 2
                # anti-clockwise
                if o1 < t + 177:
                    action_steer = 0
                # clockwise
                elif o1 > t + 183:
                    action_steer = 2
        return action_steer, action_acc

    def next_action(self, state):
        """
        Input: The current state
        Output: Action to be taken
        TO BE FILLED
        """

        # Replace with your implementation to determine actions to be taken
        # chase the end point
        action_steer, action_acc = self.chase(state,350,0)

        action = np.array([action_steer, action_acc])  

        return action

    def controller_task1(self, config_filepath=None, render_mode=False):
        """
        This is the main controller function. You can modify it as required except for the parts specifically not to be modified.
        Additionally, you can define helper functions within the class if needed for your logic.
        """
    
        ######### Do NOT modify these lines ##########
        pygame.init()
        fpsClock = pygame.time.Clock()

        if config_filepath is None:
            config_filepath = '../configs/config.json'

        simulator = DrivingEnv('T1', render_mode=render_mode, config_filepath=config_filepath)

        time.sleep(3)
        ##############################################

        # e is the number of the current episode, running it for 10 episodes
        for e in range(NUM_EPISODES):
        
            ######### Do NOT modify these lines ##########
            
            # To keep track of the number of timesteps per epoch
            cur_time = 0

            # To reset the simulator at the beginning of each episode
            state = simulator._reset()
            
            # Variable representing if you have reached the road
            road_status = False
            ##############################################

            # The following code is a basic example of the usage of the simulator
            for t in range(TIMESTEPS):
        
                # Checks for quit
                if render_mode:
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            pygame.quit()
                            sys.exit()

                action = self.next_action(state)
                state, reward, terminate, reached_road, info_dict = simulator._step(action)
                fpsClock.tick(FPS)

                cur_time += 1

                if terminate:
                    road_status = reached_road
                    break

            # Writing the output at each episode to STDOUT
            print(str(road_status) + ' ' + str(cur_time))

class Task2():

    def __init__(self):
        """
        Can modify to include variables as required
        """

        super().__init__()
        # pit locations
        self.pits = []
        # threshold distance to stay away from pit
        self.thres = 30
        # number of steps to use to steer away from pit
        self.steps = 30
        # counter for steer away
        self.count = 0
        # safe point to chase
        self.safe = [-1,-1]
    
    # rotate point (x1,y1 about (x0,y0) by angle 'th'
    def rotate(self, x0, y0, x1, y1, th):
        x1 -= x0
        y1 -= y0
        x2 = x1 * math.cos(th) - y1 * math.sin(th) + x0
        y2 = x1 * math.sin(th) + y1 * math.cos(th) + y0
        return [x2, y2]
    
    # check if position (x,y) is in a pit and if so then which pit
    def inPit(self, x, y):
        for x0, y0 in self.pits:
            x1 = x - x0
            y1 = y - y0
            if (x1 < 50 + self.thres and x1 > -50 - self.thres and y1 < 50 + self.thres and y1 > -50 - self.thres):
                return [True, x0, y0]
        return [False, -1, -1]
    
    # get points on path from state to (x2,y2)
    def path(self, state, x2, y2):
        x1, y1, _, _ = state
        r = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if x1 != x2:
            th = math.atan2(y2 - y1,x2 - x1)
        else:
            if y2 > y1:
                th = math.pi / 2
            else:
                th = -math.pi / 2
        pts = []
        for i in range(int(r / self.thres)):
            pts.append([x1 + i * self.thres * math.cos(th), y1 + i * self.thres * math.sin(th)])
        pts.append([x2,y2])
        return pts
    
    # get farthest valid/safe point on path
    def nextValid(self, path):
        i = 0
        while i < len(path):
            x, y = path[i]
            if not self.inPit(x,y)[0]:
                i += 1
            else:
                break
        if i == len(path):
            return path[-1]
        if i < 2:
            return [-1,-1]
        return path[i - 1]
    
    # steer away from pit till safe
    def steerAway(self,state):
        if self.count == self.steps or self.safe == [-1,-1]:
            self.count = 0
            self.safe = [-1,-1]
            return 1,2
        self.count += 1
        x1, y1 = self.safe
        return self.chase(state,x1,y1)
    
    # chase the point (x0,y0) (same as task 1)
    def chase(self, state, x0, y0):
        x, y, _, o = state
        # signed coordinates with respect to center of road as origin
        x1 = x - x0
        y1 = -(y - y0)
        # change orientation to (-180,180]
        if o < 180:
            o1 = -o
        else:
            o1 = 360 - o
        # direction to go
        t = math.atan2(y1,x1) * 180 / math.pi
        # car in upper half
        if t >= 0:
            # car almost aligned
            if o1 <= t - 177 and o1 >= t - 183:
                action_acc = 4
                action_steer = 1
            else:
                # steering required
                action_acc = 2
                # clockwise
                if o1 > t - 177:
                    action_steer = 2
                # anti-clockwise
                elif o1 < t - 183:
                    action_steer = 0
        # car in lower half
        else:
            # car almost aligned
            if o1 >= t + 177 and o1 <= t + 183:
                action_acc = 4
                action_steer = 1
            else:
                # steering required
                action_acc = 2
                # anti-clockwise
                if o1 < t + 177:
                    action_steer = 0
                # clockwise
                elif o1 > t + 183:
                    action_steer = 2
        return action_steer, action_acc

    def next_action(self, state):
        """
        Input: The current state
        Output: Action to be taken
        TO BE FILLED

        You can modify the function to take in extra arguments and return extra quantities apart from the ones specified if required
        """

        # Replace with your implementation to determine actions to be taken
        action_steer = 1
        action_acc = 2
        # safe to move
        if self.count == 0:
            # chase the farthest safe point
            x, y = self.nextValid(self.path(state,350,0))
            if x != -1:
                # chase till next pit
                action_steer, action_acc = self.chase(state,x,y)
            else:
                # pit encountered
                x0, y0 = self.path(state,350,0)[1]
                xp, yp = self.inPit(x0,y0)[1:]
                if y0 > 0:
                    # in lower half of board so rotate towards up
                    self.safe = self.rotate(x0,y0,xp,yp,-90)
                else:
                    # in upper half of board so rotate towards down
                    self.safe = self.rotate(x0,y0,xp,yp,90)
                self.count += 1
        else:
            # steer away from the pit
            action_steer, action_acc = self.steerAway(state)

        action = np.array([action_steer, action_acc])  

        return action

    def controller_task2(self, config_filepath=None, render_mode=False):
        """
        This is the main controller function. You can modify it as required except for the parts specifically not to be modified.
        Additionally, you can define helper functions within the class if needed for your logic.
        """
        
        ################ Do NOT modify these lines ################
        pygame.init()
        fpsClock = pygame.time.Clock()

        if config_filepath is None:
            config_filepath = '../configs/config.json'

        time.sleep(3)
        ###########################################################

        # e is the number of the current episode, running it for 10 episodes
        for e in range(NUM_EPISODES):

            ################ Setting up the environment, do NOT modify these lines ################
            # To randomly initialize centers of the traps within a determined range
            ran_cen_1x = random.randint(120, 230)
            ran_cen_1y = random.randint(120, 230)
            ran_cen_1 = [ran_cen_1x, ran_cen_1y]

            ran_cen_2x = random.randint(120, 230)
            ran_cen_2y = random.randint(-230, -120)
            ran_cen_2 = [ran_cen_2x, ran_cen_2y]

            ran_cen_3x = random.randint(-230, -120)
            ran_cen_3y = random.randint(120, 230)
            ran_cen_3 = [ran_cen_3x, ran_cen_3y]

            ran_cen_4x = random.randint(-230, -120)
            ran_cen_4y = random.randint(-230, -120)
            ran_cen_4 = [ran_cen_4x, ran_cen_4y]

            ran_cen_list = [ran_cen_1, ran_cen_2, ran_cen_3, ran_cen_4]            
            self.pits = ran_cen_list
            eligible_list = []

            # To randomly initialize the car within a determined range
            for x in range(-300, 300):
                for y in range(-300, 300):

                    if x >= (ran_cen_1x - 110) and x <= (ran_cen_1x + 110) and y >= (ran_cen_1y - 110) and y <= (ran_cen_1y + 110):
                        continue

                    if x >= (ran_cen_2x - 110) and x <= (ran_cen_2x + 110) and y >= (ran_cen_2y - 110) and y <= (ran_cen_2y + 110):
                        continue

                    if x >= (ran_cen_3x - 110) and x <= (ran_cen_3x + 110) and y >= (ran_cen_3y - 110) and y <= (ran_cen_3y + 110):
                        continue

                    if x >= (ran_cen_4x - 110) and x <= (ran_cen_4x + 110) and y >= (ran_cen_4y - 110) and y <= (ran_cen_4y + 110):
                        continue

                    eligible_list.append((x,y))

            simulator = DrivingEnv('T2', eligible_list, render_mode=render_mode, config_filepath=config_filepath, ran_cen_list=ran_cen_list)
        
            # To keep track of the number of timesteps per episode
            cur_time = 0

            # To reset the simulator at the beginning of each episode
            state = simulator._reset(eligible_list=eligible_list)
            ###########################################################

            # The following code is a basic example of the usage of the simulator
            road_status = False

            for t in range(TIMESTEPS):
        
                # Checks for quit
                if render_mode:
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            pygame.quit()
                            sys.exit()

                action = self.next_action(state)
                state, reward, terminate, reached_road, info_dict = simulator._step(action)
                fpsClock.tick(FPS)

                cur_time += 1

                if terminate:
                    road_status = reached_road
                    break

            print(str(road_status) + ' ' + str(cur_time))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="config filepath", default=None)
    parser.add_argument("-t", "--task", help="task number", choices=['T1', 'T2'])
    parser.add_argument("-r", "--random_seed", help="random seed", type=int, default=0)
    parser.add_argument("-m", "--render_mode", action='store_true')
    parser.add_argument("-f", "--frames_per_sec", help="fps", type=int, default=30) # Keep this as the default while running your simulation to visualize results
    args = parser.parse_args()

    config_filepath = args.config
    task = args.task
    random_seed = args.random_seed
    render_mode = args.render_mode
    fps = args.frames_per_sec

    FPS = fps

    random.seed(random_seed)
    np.random.seed(random_seed)

    if task == 'T1':
        
        agent = Task1()
        agent.controller_task1(config_filepath=config_filepath, render_mode=render_mode)

    else:

        agent = Task2()
        agent.controller_task2(config_filepath=config_filepath, render_mode=render_mode)
