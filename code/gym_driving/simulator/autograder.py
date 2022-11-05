#! /usr/bin/python
from email import policy
import random,argparse,sys,subprocess,os
parser = argparse.ArgumentParser()
import numpy as np

random_seeds = [13, 69, 420, 666, 42, 0, 2012, 7, 747, 8]
task1_avg = [191.2, 134.1, 176.7, 152.5, 189.6, 138.5, 162.7, 169.4, 145.5, 162.1]
task2_avg = [239.3, 224.0, 257.0, 218.6, 218.4, 238.4, 298.4, 226.0, 183.7, 225.9]
flag_ok = 0

class VerifyOutputPlanner:
    def __init__(self, task, random_seeds):
        counter = 1
        time_success_cases = 0
        road_success_cases = 0

        for seed in random_seeds:
            print('Verifying output for seed =', seed)
                
            print("\n\n","-"*100)
            cmd_planner = "python", "run_simulator.py", "--task", task, "--random_seed", str(seed), "--frames_per_sec", str(150)
            
            print('Test case', str(counter), 'seed =', str(seed), ":\t", " ".join(cmd_planner))
            
            cmd_output = subprocess.check_output(cmd_planner, universal_newlines=True)
            roadFlag, time_success = self.verifyOutput(cmd_output, task, counter-1)

            if time_success:
                time_success_cases += 1

            if roadFlag:
                road_success_cases += 1

            counter += 1

        marks = 0.1*road_success_cases + 0.15*time_success_cases
        print('Marks awarded: {}/{}'.format(marks, 2.5))

    def verifyOutput(self, cmd_output, task, counter):

        output = cmd_output.split("\n")        
        est = [i.split() for i in output if i != '']
        mistakeFlag = False
        roadFlag = True
        
        #Check 1: Checking the number of lines printed
        if not len(est) == 10:
            mistakeFlag = True
            print("\n", "*"*10, "Mistake: Exact number of lines in the standard output should be", 10, "but has", len(est), "*"*10)
            
        #Check 2: Each line should have only two values
        for i in range(len(est)):
            if not len(est[i])==2:
                mistakeFlag = True
                print("\n", "*"*10, "Mistake: On each line you should print only road status, time taken for an episode", "*"*10)
                break
        
        if not mistakeFlag:
            print("ALL CHECKS PASSED!")
        else:
            print("You haven't printed output in the correct format.")
            
        avg_time = 0
        
        for i in range(len(est)):

            road_status = est[i][0]
            time_taken = int(est[i][1])
            avg_time += time_taken

            if road_status == 'False':
                flag_ok = 1
                roadFlag = False
                print('Car does not reach the road')

            if time_taken >= 1000:
                flag_ok = 1
                roadFlag = False
                print('Car exceeds time limit')

        avg_time = avg_time/len(est)

        if task == 'T1':
            
            task1_time = task1_avg[counter]

            if avg_time < 1.1*task1_time:
                time_success = True

            else:
                print('Your car is not efficient enough')
                time_success = False

        else:

            task2_time = task2_avg[counter]

            if avg_time < 1.1*task2_time:
                time_success = True

            else:
                print('Your car is not efficient enough')
                time_success = False

        return roadFlag, time_success

            
if __name__ == "__main__":
    parser.add_argument("-t", "--task", help="task number", choices=['T1', 'T2'])
    args = parser.parse_args()

    algo = VerifyOutputPlanner(args.task, random_seeds)

    if(flag_ok):
        print("There is a mistake in Task", args.task)

