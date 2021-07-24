from gym.envs.registration import register

register(
    id='ddpg-v0',
    entry_point='ddpg.tasks:takeoff',
)

#register(
#    id='MyAgent-v0',
#    entry_point='quad_controller_rl.agent:MyAgent',
#)

#register(
#    id='RandomPolicySearch-v0',
#    entry_point='quad_controller_rl.agent:RandomPolicySearch',
#)


