class Register(object):

    def __init__(self, bits):
        self.bits = bits
        self.word = 0
        self.max_value = 1 << self.bits
        self.mask = self.max_value - 1

    def increment(self):
        self.word = (self.word + 1) % self.max_value

    def clear(self):
        self.word = 0

    def logic_and(self, word):
        self.word &= word

    def add(self, word):
        value = self.word + word
        carry = value & self.max_value
        self.word = value % self.max_value

        return 1 if carry else 0

    def complement(self):
        self.word = ~self.word & self.mask

    def shift_right(self, msb):
        lsb = self.word & 1
        self.word >>= 1
        if msb:
            msb_mask = self.max_value >> 1
            self.word |= msb_mask

        return lsb

    def shift_left(self, lsb):
        msb_mask = self.max_value >> 1
        msb = 1 if self.word & msb_mask else 0
        self.word = (self.word << 1) & self.mask
        if lsb:
            self.word |= 1

        return msb


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
        self.s = Register(1)            # Start / stop computer

    def run(self, program_start):
        self.pc.word = program_start
        self.s.word = 1

        while self.s.word == 1:
            self.tick()

    def tick(self):
        t = self.sc.word
        d = (self.ir.word >> 12) & 7
        mri = (d != 7 and t > 3)
        rri = (d == 7 and self.i.word == 0 and t == 3)

        # Instruction fetch
        if t == 0:
            self.ar.word = self.pc.word
            self.sc.increment()
        if t == 1:
            self.ir.word = self.memory_read()
            self.pc.increment()
            self.sc.increment()

        # Instruction decode
        if t == 2:
            self.ar.word = self.ir.word & 0xFFF
            self.i.word = (self.ir.word >> 15) & 1
            self.sc.increment()

        # Operand fetch
        if d != 7 and t == 3:
            if self.i.word:
                self.ar.word = self.memory_read()
            self.sc.increment()

        if mri:
            self.handle_mri(d, t)

        if rri:
            self.handle_rri(self.ir.word)

    def handle_mri(self, d, t):
        # AND
        if d == 0 and t == 4:
            self.dr.word = self.memory_read()
            self.sc.increment()
        if d == 0 and t == 5:
            self.ac.logic_and(self.dr.word)
            self.sc.clear()

        # ADD
        if d == 1 and t == 4:
            self.dr.word = self.memory_read()
            self.sc.increment()
        if d == 1 and t == 5:
            self.e.word = self.ac.add(self.dr.word)
            self.sc.clear()

        # LDA
        if d == 2 and t == 4:
            self.dr.word = self.memory_read()
            self.sc.increment()
        if d == 2 and t == 5:
            self.ac.word = self.dr.word
            self.sc.clear()

        # STA
        if d == 3 and t == 4:
            self.memory_write(self.ac)
            self.sc.clear()

        # BUN
        if d == 4 and t == 4:
            self.pc.word = self.ar.word
            self.sc.clear()

        # BSA
        if d == 5 and t == 4:
            self.memory_write(self.pc)
            self.ar.increment()
            self.sc.increment()
        if d == 5 and t == 5:
            self.pc.word = self.ar.word
            self.sc.clear()

        # ISZ
        if d == 6 and t == 4:
            self.dr.word = self.memory_read()
            self.sc.increment()
        if d == 6 and t == 5:
            self.dr.increment()
            self.sc.increment()
        if d == 6 and t == 6:
            self.memory_write(self.dr)
            if self.dr.word == 0:
                self.pc.increment()
            self.sc.clear()

    def handle_rri(self, instruction):
        # CLA
        if instruction & 0x800:
            self.ac.clear()

        # CLE
        elif instruction & 0x400:
            self.e.clear()

        # CMA
        elif instruction & 0x200:
            self.ac.complement()

        # CME
        elif instruction & 0x100:
            self.e.complement()

        # CIR
        elif instruction & 0x080:
            self.e.word = self.ac.shift_right(self.e.word)

        # CIL
        elif instruction & 0x040:
            self.e.word = self.ac.shift_left(self.e.word)

        # INC
        elif instruction & 0x020:
            self.ac.increment()

        # SPA
        elif instruction & 0x010:
            if not self.ac.word & 0x800:
                self.pc.increment()

        # SNA
        elif instruction & 0x008:
            if self.ac.word & 0x800:
                self.pc.increment()

        # SZA
        elif instruction & 0x004:
            if self.ac.word == 0:
                self.pc.increment()

        # SZE
        elif instruction & 0x002:
            if self.e.word == 0:
                self.pc.increment()

        # HLT
        elif instruction & 0x001:
            self.s.word = 0

        self.sc.clear()

    def memory_read(self):
        return self.ram.read(self.ar.word)

    def memory_write(self, register):
        self.ram.write(self.ar.word, register.word)