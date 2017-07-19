#/usr/bin/env python3

import gym
import gym_chip8.envs as _
from gym.utils.play import play

if __name__ == '__main__':
    env = gym.make("Chip8Brix-v0")
    play(env, zoom=16, fps=60)
