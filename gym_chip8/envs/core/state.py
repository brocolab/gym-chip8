import numpy as np
import binascii
from . import constants
from .display import Display


class State():
    def __init__(self, *args, **kwargs):
        self._output_has_changed = False
        self.memory = np.zeros(constants.MEMORY_SIZE, dtype=np.uint8)

        # Load the hex font
        font = np.fromstring(
            binascii.a2b_hex(constants.FONTDATA),
            dtype=np.uint8
        )
        offset = constants.FONT_OFFSET
        self.memory[offset:offset+len(font)] = font

        self.display = Display()

        self.keyboard = np.zeros(16, dtype=np.bool_)

        self.V = np.zeros(16, dtype=np.uint8)
        self.I = np.uint16()
        self.SP = np.uint8()

        self.DT = 0

        # Track changes on ST (sound events)
        self._ST = 0

        self.stack = np.zeros(16, dtype=np.uint16)

        # Set the PC to the first instruction of the ROM
        self.PC = np.uint16(constants.PROGRAM_OFFSET)

    def __getattr__(self, key):
        if key == 'ST':
            return self._ST
        else:
            super().__getattr__(key)

    def __setattr__(self, key, val):
        if key == 'ST':
            # Any changes from/to zero and nonzero are sound events
            self._output_has_changed |= bool(self._ST) ^ bool(val)
            self._ST = val
        else:
            super().__setattr__(key, val)

    def output_has_changed(self):
        result = self._output_has_changed or self.display._buffer_has_changed
        self._output_has_changed = False
        self.display._buffer_has_changed = False

        return result

    def __repr__(self):
        return 80 * '*' + '\n' + '\n'.join((
            "PC=0x{:04X}\t I=0x{:04X}\nVF=0x{:04X}\tSP=0x{:04X}".format(self.PC, self.I, self.VF, self.SP),
            "DT=0x{:04X}\tST=0x{:04X}".format(self.DT, self.ST),
            '\t'.join(["V{:02}=0x{:02X}".format(i, v) for i, v in enumerate(self.V[:8])]),
            '\t'.join(["V{:02}=0x{:02X}".format(i+8, v) for i, v in enumerate(self.V[8:])]),
            "STACK: " + ' '.join(["{:02X}".format(s) for s in self.stack]),
        )) + '\n' + 80 * '*' + '\n'
