class Register(object):
    def __init__(self, bits):
        self.bits = bits
        self.word = 0

    def inc(self):
        max_value = 1 << self.bits
        self.word = (self.word + 1) % max_value


class Memory(object):
    def __init__(self, size):
        self.data = [None] * size

    def write(self, address, word):
        self.data[address] = word

    def read(self, address):
        return self.data[address]


class Computer(object):
    def __init__(self):
        self.ram = Memory(1024 * 4)     # 4K RAM
        self.ar = Register(12)          # Address register
        self.pc = Register(12)          # Program counter
        self.dr = Register(16)          # Data register
        self.ac = Register(16)          # Accumulator
        self.ir = Register(16)          # Instruction register
        self.tr = Register(16)          # Temp register
        self.sc = Register(3)           # Sequence counter
        self.i = Register(1)            # Decode bit
        self.e = Register(1)            # Carry bit

