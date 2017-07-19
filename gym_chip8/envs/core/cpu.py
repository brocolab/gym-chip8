from . import utils
from . import state
from . import opcodes
from .constants import SZ_INSTR


class OpcodeTable(object):
    __metaclass__ = utils.Singleton

    opcodes = None
    hooked = None

    def __init__(self, opmodule):
        self.opcodes = dict()
        self.hooked = dict()
        self.opmap = dict()
        self.load_module(opmodule)

    def load_module(self, opmod):
        #path = os.path.basename(opmod).strip('.py')
        #opmod = importlib.import_module('.%s' % path, 'core')
        for key in opmod.__dict__:
            if key.startswith('op_'):
                opcode = key[3:]
                method = opmod.__dict__[key]
                self.opcodes[opcode] = method

    def get_opcode_key(self, opcode):
        n1 = opcode >> 0xC
        n2 = (opcode & 0xF00) >> 0x8
        n3 = (opcode & 0xF0) >> 0x4
        n4 = (opcode & 0xF)

        #print(hex(opcode), hex(n1), hex(n2), hex(n3), hex(n4))

        if n1 == 0x0:
            if n2 != 0x0:
                return '0nnn'
            elif n4 == 0x0:
                return '00E0'
            elif n4 == 0xE:
                return '00EE'
        elif n1 in [0x1, 0x2, 0xA, 0xB]:
            return '%Xnnn' % n1
        elif n1 in [0x3, 0x4, 0x6, 0x7, 0xC]:
            return '%Xxkk' % n1
        elif n1 in [0x5, 0x9]:
            return '%Xxy0' % n1
        elif n1 == 0x8:
            if n4 in [0, 1, 2, 3, 4, 5, 6, 7, 0xE]:
                return '8xy%X' % n4
        elif n1 == 0xD:
            return 'Dxyn'
        elif n1 == 0xE:
            if n4 == 0xE:
                return 'Ex9E'
            elif n4 == 0x1:
                return 'ExA1'
        elif n1 == 0xF:
            if n3 in [0x0, 0x1, 0x2, 0x3, 0x5, 0x6]:
                if n4 in [0x3, 0x5, 0x7, 0xA, 0x8, 0xE, 0x9]:
                    return 'Fx%X%X' % (n3, n4)

        raise KeyError('Invalid OpCode: 0x%X' % opcode)

    def hook(self, key, handler):
        original = self.opcodes[key]
        self.hooked[key] = original
        self.opcodes[key] = handler

    def unhook(self, key):
        self.opcodes[key] = self.hooked[key]
        del self.hooked[key]

    def pre_hook(self, key, handler):
        original = self.opcodes[key]

        def handle(state):
            handler(state)
            original(state)

        self.hook(key, handle)

    def post_hook(self, key, handler):
        original = self.opcodes[key]

        def handle(state):
            original(state)
            handler(state)

        self.hook(key, handle)

    def __getitem__(self, key):
        key = self.get_opcode_key(key)
        return self.opcodes[key]

    def __setitem__(self, key, value):
        self.hook(key, value)

    def __delitem__(self, opcode):
        key = self.get_opcode_key(opcode)
        if key in self.hooked:
            self.unhook(opcode)

    def __call__(self, key, *args, **kwargs):
        return self.__getitem__(key)


class CPU(object):
    state = None
    optable = None

    def __init__(self, current=None):
        self.optable = OpcodeTable(opcodes)

        if current is not None:
            self.state = current
        else:
            self.state = state.State()

    def fetch_instruction(self):
        # Reverse MSB order
        msb = self.state.memory[self.state.PC] << 8
        lsb = self.state.memory[self.state.PC + 1]

        # Increase the program counter
        self.state.PC += SZ_INSTR

        return msb + lsb

    def step(self):
        self.state.current = self.fetch_instruction()
        try:
            self.optable[self.state.current](self.state)
        except KeyError as ex:
            print('[!] ERROR: unknown opcode: %s' % str(ex))
