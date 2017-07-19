#!/usr/bin/env python3

import sys
import os
import time

import core.vm as vmlib

VM      = None
DISPLAY = None


def clear_terminal():
    '''refresh the terminal output'''
    sys.stdout.write("\x1b[2J\x1b[H")

def cycle():
    '''run a batch of instructions based on the CPU clock'''
    clear_terminal()
    VM.cycle()
    display()

def display():
    '''print the display buffer'''
    print(DISPLAY)

def step():
    '''execute next instruction'''
    VM.cpu.step()

def add_breakpoint(addr):
    '''insert breakpoint at addr'''
    return True

def remove_breakpoint(addr):
    '''remove breakpoint at addr'''
    return True

def search_memory(pattern, start=0, end=0x1000):
    '''search memory for a pattern'''
    return True

def cont():
    '''continue execution'''
    try:
        while True: step()
    except KeyboardInterrupt():
        pass

def aux_print_help():
    print('\nCHIP-8 Interactive Debugger (c8idb) - v.0.1\n')
    current = globals()
    print('global helper variables:')
    for key in current:
        if key.startswith('__'):
            continue
        if key.upper() == key:
            print('\t', key)
    print()
    print('available functions:')
    for key in current:
        if key.startswith('aux_'):
            continue
        value = current[key]
        if callable(value):
            if not hasattr(value, '__doc__'):
                continue
            print('\t', key, '-', value.__doc__)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        name = 'INVADERS'
    else:
        name = str(sys.argv[1]).upper()

    global VM
    global DISPLAY

    VM = vmlib.VM()
    path = os.path.abspath("roms/%s" % name)
    VM.load_rom(path)

    DISPLAY= VM.get_display()

    aux_print_help()
