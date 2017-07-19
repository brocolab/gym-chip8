# CHIP-8 AI learning environment for OpenAI Gym

## Installation

    cd gym-chip8
    pip install -e .

You will need to `import gym_chip8` before using so that Gym registers the
environment.

## Available environments:

- `Chip8Brix-v0`

    The game BRIX. The reward function is the score increase between steps.

(more coming)

## Example usage

See `random_agent.py` for typical training usage.

It's also possible to test the environment by playing interactively using
`gym.utils.play`. See `play.py` for an example (requires `pygame` and
`matplotlib` to be installed).

## License

The MIT License

Copyright (c) 2017 brocolab