import gym
import gym_chip8 as _


class RandomAgent(object):
    """The world's simplest agent!"""
    def __init__(self, action_space):
        self.action_space = action_space

    def act(self, observation, reward, done):
        return self.action_space.sample()


if __name__ == '__main__':
    env = gym.make('Chip8Brix-v0')

    agent = RandomAgent(env.action_space)

    episode_count = 1000
    reward = 0
    done = False

    for i in range(episode_count):
        ob = env.reset()
        while True:
            action = agent.act(ob, reward, done)
            ob, reward, done, vars = env.step(action)

            env.render()
            if done:
                break

    env.close()
