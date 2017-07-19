import numpy as np
from . import constants


class Display():
    def __init__(self, *args, **kwargs):
        self._buffer_has_changed = False

        shape = constants.SCREEN_ROWS, constants.SCREEN_COLS
        self.buffer = np.zeros(shape, *args, dtype=np.uint8, **kwargs)

    def clear(self):
        self._buffer_has_changed = np.any(self.buffer)
        self.buffer.fill(0)

    def draw_sprite(self, x, y, sprite):
        self._buffer_has_changed = True

        collision = False
        # Each byte is a row of 8 pixels
        for row, byte in enumerate(sprite):
            # Skip rows beyond the bottom of the screen
            if y + row >= constants.SCREEN_ROWS:
                continue

            # Skip if the initial column coordinate is beyond the right limit
            if x >= constants.SCREEN_COLS:
                continue

            xmax = min(x + 8, constants.SCREEN_COLS)
            numcols = xmax - x
            mask = np.unpackbits(byte)[:numcols]

            old_pixel_row = self.buffer[y+row][x:xmax]
            # A collision occurs when at least one pixel is about to be erased
            collision |= np.any(np.bitwise_and(old_pixel_row, mask))

            # XOR each pixel of the sprite row with the buffer
            self.buffer[y+row][x:xmax] = np.bitwise_xor(old_pixel_row, mask)

            # A change occures when at least one pixel is flipped
            self._buffer_has_changed |= (self.buffer[y+row][x:xmax] != old_pixel_row).any()

        return collision

    def __repr__(self):
        result = ""
        result += '.' + constants.SCREEN_COLS * '-' + '.\n'
        for row in range(constants.SCREEN_ROWS):
            result += '|'
            for col in range(constants.SCREEN_COLS):
                result += '#' if self.buffer[row][col] else ' '
            result += '|\n'
        result += "'" + constants.SCREEN_COLS * '-' + "'\n"
        return result
