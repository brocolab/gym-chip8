import numpy as np

import os
import gym

from gym import error, spaces
from gym import utils

from gym.utils import seeding

from .core.vm import VM
from .core.constants import *

import logging
logger = logging.getLogger(__name__)

SCALE = 8


class Chip8Env(gym.Env):
    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self, game, frameskip=0):
        self.frameskip = frameskip
        self.viewer = None

        dir_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(dir_path, "roms/%s.json" % game)
        if not os.path.exists(path):
            raise IOError('You asked for game %s but path %s does not exist' % (game, path))
        self._rom_profile_path = path

        self.vm = VM(frame_limiting=False)
        self.reset()

        self.action_space = spaces.Discrete(self.vm.get_num_actions())
        self.observation_space = spaces.Box(low=0, high=1, shape=(SCREEN_ROWS, SCREEN_COLS))

    def _get_frame_reward(self, frame):
        raise NotImplementedError

    def _get_done(self, frame):
        raise NotImplementedError

    def _step(self, action):
        if self.frameskip:
            num_steps = self.frameskip + 1
        else:
            num_steps = 1

        frame = None
        reward = 0
        for _ in range(num_steps):
            self.vm.take_action(action)
            frame = next(self.vm.frames())
            reward += self._get_frame_reward(frame)

        observation = frame.buffer
        done = self._get_done(frame)

        return observation, reward, done, frame.variables

    def _get_img(self):
        im = self.vm.get_display_buffer()
        # Scale the 2D array before converting to RGB
        im = np.kron(im, np.ones((SCALE, SCALE)))
        w, h = im.shape
        ret = np.empty((w, h, 3), dtype=np.uint8)
        ret[:, :, 0] = im*255
        ret[:, :, 1] = im*255
        ret[:, :, 2] = im*255

        return ret

    def _reset(self):
        self.vm.reset()
        self.vm.load_rom_profile(self._rom_profile_path)
        return self._get_img()

    def get_keys_to_action(self):
        # Used by gym.utils.play
        actions = ((),) + tuple((ord(c),) for c in "1234qwerasdfzxcv")
        return dict([(v, k) for k, v in enumerate(actions)])

    def _render(self, mode='human', close=False):
        if close:
            if self.viewer is not None:
                self.viewer.close()
                self.viewer = None
            return
        img = self._get_img()

        if mode == 'rgb_array':
            return img
        elif mode == 'human':
            from gym.envs.classic_control import rendering
            if self.viewer is None:
                self.viewer = rendering.SimpleImageViewer()
            self.viewer.imshow(img)


class Chip8BrixEnv(Chip8Env):
    def __init__(self, *args, **kwargs):
        super().__init__('BRIX', *args, **kwargs)
        self._previous_score = 0

    def get_keys_to_action(self):
        actions = ((),) + tuple((ord(c),) for c in "qe")
        return dict([(v, k) for k, v in enumerate(actions)])

    def _get_frame_reward(self, frame):
            # Hand out a reward of 1 when the score is increased
            # (no negative rewards are given for losing lives)
            score = frame.variables["score"]
            reward = max(0, score - self._previous_score)
            self._previous_score = score

            return reward

    def _get_done(self, frame):
        return frame.cycle_index > 0 and frame.variables["balls_remaining"] == 0
