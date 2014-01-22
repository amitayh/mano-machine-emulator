from amitayh.mano.logger import Logger


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
        self.e = Register(1)            # Carry bit
        self.s = Register(1)            # Start / stop computer
        self.logger = Logger()          # Default simple logger

    def run(self, program_start):
        self.pc.word = program_start
        self.s.word = 1
        while self.s.word == 1:
            self.tick()

    def tick(self):
        t = self.sc.word
        d = (self.ir.word >> 12) & 7    # IR(12-14)
        i = (self.ir.word >> 15) & 1    # IR(15)

        # Instruction fetch
        if t == 0:
            self.logger.log("R'T0: AR <- PC")
            self.ar.word = self.pc.word
            self.sc.increment()
        if t == 1:
            self.logger.log("R'T1: IR <- M[AR], PC <- PC + 1")
            self.ir.word = self.memory_read()
            self.pc.increment()
            self.sc.increment()

        # Instruction decode
        if t == 2:
            self.logger.log("R'T2: AR <- IR(0-11)")
            self.ar.word = self.ir.word & 0xFFF
            self.sc.increment()

        # Operand fetch
        if t == 3 and d != 7:
            if i:
                self.logger.log("D7'IT3: AR <- M[AR]")
                self.ar.word = self.memory_read()
            else:
                self.logger.log("D7'I'T3: NOOP")
            self.sc.increment()

        # Execute
        if t > 3 and d != 7:
            self.execute_mri(d, t)
        if t == 3 and d == 7 and i == 0:
            self.execute_rri(self.ir.word)

    def execute_mri(self, d, t):
        # AND
        if d == 0 and t == 4:
            self.logger.log("D0T4: DR <- M[AR]")
            self.dr.word = self.memory_read()
            self.sc.increment()
        if d == 0 and t == 5:
            self.logger.log("D0T5: AC <- AC & DR, SC <- 0")
            self.ac.logic_and(self.dr.word)
            self.sc.clear()

        # ADD
        if d == 1 and t == 4:
            self.logger.log("D1T4: DR <- M[AR]")
            self.dr.word = self.memory_read()
            self.sc.increment()
        if d == 1 and t == 5:
            self.logger.log("D1T5: AC <- AC + DR, E <- Cout, SC <- 0")
            self.e.word = self.ac.add(self.dr.word)
            self.sc.clear()

        # LDA
        if d == 2 and t == 4:
            self.logger.log("D2T4: DR <- M[AR]")
            self.dr.word = self.memory_read()
            self.sc.increment()
        if d == 2 and t == 5:
            self.logger.log("D2T4: AC <- DR, SC <- 0")
            self.ac.word = self.dr.word
            self.sc.clear()

        # STA
        if d == 3 and t == 4:
            self.logger.log("D3T4: M[AR] <- AC, SC <- 0")
            self.memory_write(self.ac)
            self.sc.clear()

        # BUN
        if d == 4 and t == 4:
            self.logger.log("D4T4: PC <- AR, SC <- 0")
            self.pc.word = self.ar.word
            self.sc.clear()

        # BSA
        if d == 5 and t == 4:
            self.logger.log("D5T4: M[AR] <- PC, AR <- AR + 1")
            self.memory_write(self.pc)
            self.ar.increment()
            self.sc.increment()
        if d == 5 and t == 5:
            self.logger.log("D5T5: PC <- AR, SC <- 0")
            self.pc.word = self.ar.word
            self.sc.clear()

        # ISZ
        if d == 6 and t == 4:
            self.logger.log("D6T4: DR <- M[AR]")
            self.dr.word = self.memory_read()
            self.sc.increment()
        if d == 6 and t == 5:
            self.logger.log("D6T5: DR <- DR + 1")
            self.dr.increment()
            self.sc.increment()
        if d == 6 and t == 6:
            self.logger.log("D6T6: M[AR] <- DR, if (DR = 0) then (PC <- PC + 1), SC <- 0")
            self.memory_write(self.dr)
            if self.dr.word == 0:
                self.pc.increment()
            self.sc.clear()

    def execute_rri(self, instruction):
        # CLA
        if instruction & 0x800:
            self.logger.log("D7I'T3B11: AC <- 0, SC <- 0")
            self.ac.clear()

        # CLE
        elif instruction & 0x400:
            self.logger.log("D7I'T3B10: E <- 0, SC <- 0")
            self.e.clear()

        # CMA
        elif instruction & 0x200:
            self.logger.log("D7I'T3B9: AC <- AC', SC <- 0")
            self.ac.complement()

        # CME
        elif instruction & 0x100:
            self.logger.log("D7I'T3B8: E <- E', SC <- 0")
            self.e.complement()

        # CIR
        elif instruction & 0x080:
            self.logger.log("D7I'T3B7: AC <- shr(AC), AC(15) <- E, E <- AC(0), SC <- 0")
            self.e.word = self.ac.shift_right(self.e.word)

        # CIL
        elif instruction & 0x040:
            self.logger.log("D7I'T3B6: AC <- shl(AC), AC(0) <- E, E <- AC(15), SC <- 0")
            self.e.word = self.ac.shift_left(self.e.word)

        # INC
        elif instruction & 0x020:
            self.logger.log("D7I'T3B5: AC <- AC + 1, SC <- 0")
            self.ac.increment()

        # SPA
        elif instruction & 0x010:
            self.logger.log("D7I'T3B4: if (AC(15) = 0) then (PC <- PC + 1), SC <- 0")
            if not self.ac.word & 0x800:
                self.pc.increment()

        # SNA
        elif instruction & 0x008:
            self.logger.log("D7I'T3B3: if (AC(15) = 1) then (PC <- PC + 1), SC <- 0")
            if self.ac.word & 0x800:
                self.pc.increment()

        # SZA
        elif instruction & 0x004:
            self.logger.log("D7I'T3B2: if (AC = 0) then (PC <- PC + 1), SC <- 0")
            if self.ac.word == 0:
                self.pc.increment()

        # SZE
        elif instruction & 0x002:
            self.logger.log("D7I'T3B1: if (E = 0) then (PC <- PC + 1), SC <- 0")
            if self.e.word == 0:
                self.pc.increment()

        # HLT
        elif instruction & 0x001:
            self.logger.log("D7I'T3B0: S <- 0, SC <- 0")
            self.s.word = 0

        self.sc.clear()

    def memory_read(self):
        return self.ram.read(self.ar.word)

    def memory_write(self, register):
        self.ram.write(self.ar.word, register.word)