from numpy.lib.utils import info
import random
from gym import Env
from gym import envs
import gym
from gym.spaces import Discrete, Box
import stable_baselines3
from stable_baselines3 import A2C
from stable_baselines3.common.env_util import make_vec_env
from gym import spaces
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv, subproc_vec_env
from stable_baselines3.common.utils import set_random_seed
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.env_util import make_vec_env
from typing import Callable
from stable_baselines3 import PPO
import os
import gym
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import TD3
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.results_plotter import load_results, ts2xy
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common import results_plotter
from stable_baselines3.common import monitor
import torch as th
from Snake import Snake


############### GAME CODE NOW IN GYM FOLDER AS REGISTERED ENV #####################################################


################ LEARNING RATE SCHEUDULE

# def linear_schedule(initial_value: float) -> Callable[[float], float]:
#     """
#     Linear learning rate schedule.

#     :param initial_value: Initial learning rate.
#     :return: schedule that computes
#       current learning rate depending on remaining progress
#     """
#     def func(progress_remaining: float) -> float:
#         """
#         Progress will decrease from 1 (beginning) to 0.

#         :param progress_remaining:
#         :return: current learning rate
#         """
#         return (progress_remaining+0.1)*initial_value

#     return func



#CUSTOM AI ARCHITECTURE

policy_kwargs = dict(activation_fn=th.nn.ReLU,
                     net_arch=[256, dict(pi=[128], vf=[128])])

#CUSTOM AI ARCHITECTURE



# **************************************** AI PORTION *********************************************************'

def make_env(env_id: str, rank: int, seed: int = 0) -> Callable:
    """
    Utility function for multiprocessed env.
    
    :param env_id: (str) the environment ID
    :param num_env: (int) the number of environment you wish to have in subprocesses
    :param seed: (int) the inital seed for RNG
    :param rank: (int) index of the subprocess
    :return: (Callable)
    """
    def _init() -> gym.Env:
        #Monitor gives us rewards and episode lengths
        env = Monitor(Snake())
        env.seed(seed + rank)
        return env
    set_random_seed(seed)
    return _init

if __name__=="__main__":
    env_id = "Snake-v0"
    num_cpu = 1 # Number of processes to use
    # Create the vectorized environment
    env = SubprocVecEnv([make_env(env_id, i) for i in range(num_cpu)])

    #Learning rate of 0.0008 seems to be the best and its not even close.
    model = PPO('MlpPolicy', env, policy_kwargs=policy_kwargs, verbose=1,tensorboard_log="/a2c_cartpole_tensorboard/",learning_rate=0.0007)

#Training

    # model.learn(total_timesteps=5000000)
    # model.save("a2c_cartpole3")

#Loading

    model = PPO.load("a2c_cartpole3")

    obs = env.reset()

    while True:
        action, _states = model.predict(obs)
        obs, rewards, dones, info = env.step(action)
        # env.render()



# RUN THIS TO LOG, MAKE SURE CMD IS IN e WEBDEV SNAKEAI (AKA gamefolder)
# tensorboard --logdir /a2c_cartpole_tensorboard/ 

