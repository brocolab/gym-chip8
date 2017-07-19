import os
import json
import time
import numpy as np
from .cpu import CPU
from .state import State
from . import constants


NO_ACTION = -1

class Frame():
    def __init__(self, cycle_index, buffer, buzzer_state, delta, variables=None):
        self.cycle_index = cycle_index
        self.buffer = buffer
        self.buzzer_state = buzzer_state
        self.delta = delta
        self.variables = variables


class VM():
    def __init__(self, *args, frame_limiting=False, **kwargs):
        self._profile = {}
        self._frame_limiting = frame_limiting
        self._keypress_queue = []
        self.reset()

    def reset(self):
        self._current_cycle = 0
        self.state = State()
        self.cpu = CPU(self.state)
        #self.cpu.post_hook('Fx18', sound_hook)
        self._last_cycle_timestamp = time.time()

    def load_rom(self, path):
        rom = np.fromfile(path, dtype=np.uint8)

        # Assign the ROM array directly to the program code offset
        offset = constants.PROGRAM_OFFSET
        self.state.memory[offset:offset+len(rom)] = rom

    def load_rom_profile(self, path):
        with open(path) as profile_file:
            self._profile = json.load(profile_file)
            rompath = os.path.join(os.path.dirname(path), self._profile["rom"])
            self.load_rom(rompath)

    def get_display(self):
        return self.state.display

    def get_buzzer_state(self):
        return self.state.ST > 0

    def get_display_buffer(self):
        return np.copy(self.state.display.buffer)

    def get_variable(self, name):
        # Throw a key error on purpose here if the variable is not defined
        variable_profile = self._profile["variables"][name]
        vartype = variable_profile["type"]
        index = variable_profile["index"]

        if vartype == "mem_bcd":
            hundreds = self.state.memory[index]
            tens = self.state.memory[index+1]
            ones = self.state.memory[index+2]

            return hundreds * 100 + tens * 10 + ones

        elif vartype == "register":
            return self.state.V[index]

        else:
            raise ValueError("Unknown variable type: " + vartype)

    def get_frame(self):
        variables = {}
        if 'variables' in self._profile:
            variables = dict((v, self.get_variable(v)) for v in self._profile["variables"])

        return Frame(self._current_cycle,
                     self.get_display_buffer(),
                     self.get_buzzer_state(),
                     self.state.output_has_changed(),
                     variables=variables)

    def key_down(self, key_index):
        self.state.keyboard[key_index] = 1

    def key_up(self, key_index):
        self.state.keyboard[key_index] = 0

    def get_num_actions(self):
        # Throw a key error on purpose here if no actions are defined
        key_actions = self._profile["actions"]

        # +1 for "take no action"
        return len(key_actions) + 1

    def take_action(self, action_index):
        key_actions = self._profile["actions"]
        actions = [NO_ACTION] + key_actions
        action = actions[action_index]

        if action != NO_ACTION:
            self._keypress_queue.append(action)

    def enable_frame_limiting(self):
        self._frame_limiting = True

    def disable_frame_limiting(self):
        self._frame_limiting = False

    def cycle(self):
        # Cycles normally occur at a 60Hz frequency

        # Keypress are key events that last for a single frame
        pressed_key = None
        if self._keypress_queue:
            pressed_key = self._keypress_queue.pop(0)
            self.state.keyboard[pressed_key] = 0x1

        # The CPU clock should be around ~500Hz, so we set
        # INSTRUCTIONS_PER_CYCLE = 9
        for _ in range(constants.INSTRUCTIONS_PER_CYCLE):
            self.cpu.step()

        if self.state.DT > 0:
            self.state.DT -= 1

        if self.state.ST > 0:
            self.state.ST -= 1

        # If frame limiting is enabled, sleep for the rest of the cycle period
        if self._frame_limiting:
            ellapsed = time.time() - self._last_cycle_timestamp
            remaining = 1.0/constants.FREQUENCY - ellapsed
            if remaining > 0:
                time.sleep(remaining)

        self._current_cycle += 1
        self._last_cycle_timestamp = time.time()

        # Stop pressing the key after the frame is over
        if pressed_key is not None:
            self.state.keyboard[pressed_key] = 0x0

    def frames(self):
        while True:
            self.cycle()
            yield self.get_frame()
