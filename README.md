# RL-drone-with-ros-ddpg-and-unity

to run the project

$ git clone https://github.com/Excurrybang/RL-drone-with-ros-ddpg-and-unity

$ cd project_rl

$ catkin_make

$ source devel/setup.bash

$ cd src/orchestrator/scripts

$ chmod +x connect

$ chmod +x handelNode

put the folder RL-drone-with-ros-ddpg-and-unity/orchestrator under project_rl/devel/lib

$ conda activate iros

$ roslaunch orchestrator run.launch
