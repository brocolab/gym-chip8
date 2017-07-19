import numpy as np
import random
from . import constants

SZ_INSTR = constants.SZ_INSTR


def n1(i):
    return i >> 0xC


def x(i):
    return (i & 0x0F00) >> 0x8


def y(i):
    return (i & 0x00F0) >> 0x4


def n(i):
    return i & 0x000F


def kk(i):
    return i & 0x00FF


def nnn(i):
    return i & 0x0FFF


def op_00E0(st):
    '''CLS'''
    st.display.clear()


def op_00EE(st):
    '''RET'''
    st.SP -= 1
    st.PC = st.stack[st.SP]


def op_0nnn(st):
    '''SYS addr'''
    # ignore
    pass


def op_1nnn(st):
    '''JP addr'''
    c = st.current
    st.PC = nnn(c)


def op_2nnn(st):
    # CALL nnn
    c = st.current
    st.stack[st.SP] = st.PC
    st.SP += 1
    st.PC = nnn(c)


def op_3xkk(st):
    # SE Vx, kk
    c = st.current
    if np.equal(st.V[x(c)], kk(c)):
        st.PC += SZ_INSTR


def op_4xkk(st):
    # SNE Vx, kk
    c = st.current
    if np.not_equal(st.V[x(c)], kk(c)):
        st.PC += SZ_INSTR


def op_5xy0(st):
    # SE Vx, Vy
    c = st.current
    if np.equal(st.V[x(c)], st.V[y(c)]):
        st.PC += SZ_INSTR


def op_6xkk(st):
    # LD Vx, kk
    c = st.current
    st.V[x(c)] = kk(c)


def op_7xkk(st):
    # ADD Vx, kk
    c = st.current
    st.V[x(c)] = np.add(st.V[x(c)], kk(c))


def op_8xy0(st):
    # LD Vx, Vy
    c = st.current
    st.V[x(c)] = st.V[y(c)]


def op_8xy1(st):
    # OR Vx, Vy
    c = st.current
    st.V[x(c)] = np.bitwise_or(st.V[x(c)], st.V[y(c)])


def op_8xy2(st):
    # AND Vx, Vy
    c = st.current
    st.V[x(c)] = np.bitwise_and(st.V[x(c)], st.V[y(c)])


def op_8xy3(st):
    # XOR Vx, Vy
    c = st.current
    st.V[x(c)] = np.bitwise_xor(st.V[x(c)], st.V[y(c)])


def op_8xy4(st):
    # ADD Vx, Vy
    c = st.current
    actual = int(st.V[x(c)]) + int(st.V[y(c)])
    if actual > 0xFF:
        st.V[0xF] = np.uint8(1)
    else:
        st.V[0xF] = np.uint8(0)
    st.V[x(c)] = np.add(st.V[x(c)], st.V[y(c)])


def op_8xy5(st):
    # SUB Vx, Vy
    c = st.current
    if st.V[y(c)] > st.V[x(c)]:
        st.V[0xF] = np.uint8(0)
    else:
        st.V[0xF] = np.uint8(1)
    st.V[x(c)] = np.subtract(st.V[x(c)], st.V[y(c)])


def op_8xy6(st):
    # SHR Vx {, Vy}
    c = st.current
    if st.V[x(c)] & 0x1:
        st.V[0xF] = np.uint8(1)
    else:
        st.V[0xF] = np.uint8(0)
    st.V[x(c)] = np.right_shift(st.V[x(c)], 1)


def op_8xy7(st):
    # SUBN Vx, Vy
    c = st.current
    if st.V[x(c)] > st.V[y(c)]:
        st.V[0xF] = np.uint8(0)
    else:
        st.V[0xF] = np.uint8(1)
    st.V[y(c)] = np.subtract(st.V[y(c)], st.V[x(c)])


def op_8xyE(st):
    # SHL Vx {, Vy}
    c = st.current
    if st.V[x(c)] & 0x80:
        st.V[0xF] = np.uint8(1)
    else:
        st.V[0xF] = np.uint8(0)
    st.V[x(c)] = np.left_shift(st.V[x(c)], 1)


def op_9xy0(st):
    # SNE Vx, Vy
    c = st.current
    if np.not_equal(st.V[x(c)], st.V[y(c)]):
        st.PC += SZ_INSTR


def op_Annn(st):
    # LD I, nnn
    c = st.current
    st.I = nnn(c)


def op_Bnnn(st):
    # JP V0, nnn
    c = st.current
    st.PC = np.add(np.uint16(st.V[0]), nnn(c))


def op_Cxkk(st):
    # RND Vx, kk
    c = st.current
    st.V[x(c)] = np.bitwise_and(np.uint8(random.random() * 0xFF), kk(c))


def op_Dxyn(st):
    # DRW Vx, Vy, n
    c = st.current
    sprite = st.memory[st.I:st.I+n(c)]
    collision = st.display.draw_sprite(st.V[x(c)], st.V[y(c)], sprite)
    st.V[0xF] = np.uint8(collision)


def op_Ex9E(st):
    # SKP Vx
    c = st.current
    if st.keyboard[st.V[x(c)]]:
        st.PC += SZ_INSTR


def op_ExA1(st):
    # SKNP Vx
    c = st.current
    if not st.keyboard[st.V[x(c)]]:
        st.PC += SZ_INSTR


def op_Fx07(st):
    # LD Vx, DT
    c = st.current
    st.V[x(c)] = st.DT


def op_Fx0A(st):
    # LD Vx, K
    c = st.current
    if np.any(st.keyboard):
        K = st.keyboard.nonzero()[0][0]
        st.V[x(c)] = np.uint8(K)
    else:
        # PC is not incremented until a key is pressed
        st.PC -= SZ_INSTR


def op_Fx15(st):
    # LD DT, Vx
    c = st.current
    st.DT = st.V[x(c)]


def op_Fx18(st):
    # LD ST, Vx
    c = st.current
    st.ST = st.V[x(c)]


def op_Fx1E(st):
    # ADD I, Vx
    c = st.current
    actual = int(st.I) + int(st.V[x(c)])
    if actual > 0xFFFF:
        st.V[0xF] = np.uint8(1)
    else:
        st.V[0xF] = np.uint8(0)
    st.I = np.add(st.I, st.V[x(c)])


def op_Fx29(st):
    # LD F, Vx
    c = st.current
    st.I = constants.FONT_OFFSET + np.uint16(st.V[x(c)]) * constants.FONT_SIZE


def op_Fx33(st):
    # LD B, Vx
    c = st.current
    st.memory[st.I] = st.V[x(c)] // 100
    st.memory[st.I+1] = (st.V[x(c)] % 100) // 10
    st.memory[st.I+2] = st.V[x(c)] % 10


def op_Fx55(st):
    # LD [I], Vx
    c = st.current
    for i in range(x(c)+1):
        st.memory[st.I+i] = st.V[i]


def op_Fx65(st):
    # LD Vx, [I]
    c = st.current
    for i in range(x(c)+1):
        st.V[i] = st.memory[st.I+i]
