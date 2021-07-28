# Group-Project-Quadrotor-RL

Use ROS with DDPG reinforcement-learning algorithm to control a simulated quadrotor in Unity， written by python

to run the project

$ git clone https://github.com/Excurrybang/Group-Project-Quadrotor-RL

$ cd project_rl

$ catkin_make

$ source devel/setup.bash

$ cd src/orchestrator/scripts

$ chmod +x connect

$ chmod +x handelNode

put the folder Group-Project-Quadrotor-RL/orchestrator under project_rl/devel/lib

$ cd project/devel/lib/orchestrator

$ chmod +x Linux_build.x86_64

$ conda activate iros

$ roslaunch orchestrator run.launch
