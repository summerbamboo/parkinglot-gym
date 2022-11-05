# parking-lot

Repository for the course project done as part of CS-747 (Foundations of Intelligent & Learning Agents) course at IIT Bombay in Autumn 2022.  
Webpage: https://sarthakmittal92.github.io/projects/aut22/parking-lot/

## Overview
This assignment tests your understanding of the concepts taught in class and its applications to real world problems. In particular, we examine one of the most popular domains: **autonomous driving**. You will have to come up with a controller to drive a car, and are free to use any approach: coding it up yourself and/or learning with value function-based approaches and/or using policy search.

There are two tasks in this assignment. In Task 1, you will construct a controller that can navigate a car out of a parking lot on a winter night. The surroundings are icy and the parking lot is also close to freezing. It is your responsibility to get the car out of this situation and on the road safely. Task 2 is along similar lines but you find yourself in a stickier situation. The parking lot is now filled with pools of mud from a cold winter storm. You must dodge these obstacles and find a safe way out.

All the code you write for this assignment must be in Python 3.8.10. The libraries that you require come installed with the docker image that has been shared for the course, and are already imported in the files you need to complete.

## Code Structure
[This compressed directory](https://www.cse.iitb.ac.in/~shivaram/teaching/cs747-a2022/pa-3/gym_driving_dir.tar.gz) has all the files and folders that are required for the assignment (we acknowledge Wesley Hsieh for a [base simulator](https://github.com/WesleyHsieh/gym-driving) that our assignment is built upon). For the most part, you do not need to worry about these files. It is, however, advised that you read through `driving_env.py` in the envs folder to understand how the `_step` function works. In short, it returns the reward, termination condition, the next state and a boolean flag to indicate the success of the episode (it also returns a dictionary with additional information that can be ignored). In addition to the above, the `_reset` function of the simulator resets the environment and returns the initial state of the car.

We have provided `run_simulator.py` to run simulations and visually see the working of your controller, which you’ll have to submit as described later. This code has been provided with 10 random seeds that evaluate your controllers for a fixed few environments (different initial states of your car and different positions of the obstacles in Task 2) and outputs the execution time. The only file you need to edit is `run_simulator.py`. Do not edit any other files.

For evaluation, we will use another set of environments in the autograder, and use its score as is for the evaluation. See the exact details below.

## Report
Unlike the previous assignments, you have been given a free hand to come up with your controller. Hence, we would like to see a clear presentation of your approach. Include a file named `report.pdf` that spells out the ingredients of your solution, any intermediate experiments that may have guided your decisions, learning curves if you did use some form of learning/parameter tuning, and so on. If your report is not sufficiently clear and informative, you will stand to lose marks.

## Complete Problem
The full problem statement is accessible here: [CS747 Programming Assignment 3](https://hackmd.io/@sarthakmittal/Bk1Z7pzVi)
