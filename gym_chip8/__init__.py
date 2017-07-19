import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)

register(
    id='Chip8Brix-v0',
    entry_point='gym_chip8.envs:Chip8BrixEnv',
    timestep_limit=100000,
)