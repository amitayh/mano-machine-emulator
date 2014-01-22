from unittest import TestCase
from amitayh.mano.assembler import Assembler
from amitayh.mano.computer import Register, Memory, Computer


class TestRegister(TestCase):
    def test_increment(self):
        register = Register(3)
        register.word = 5

        register.increment()
        self.assertEquals(6, register.word)

        register.increment()
        self.assertEquals(7, register.word)

        register.increment()
        self.assertEquals(0, register.word)

    def test_clear(self):
        register = Register(3)
        register.word = 5

        register.clear()
        self.assertEquals(0, register.word)

    def test_logic_and(self):
        register = Register(3)
        register.word = 5

        register.logic_and(6)
        self.assertEquals(5 & 6, register.word)

    def test_add(self):
        register = Register(3)
        register.word = 5

        carry = register.add(6)
        self.assertEquals(1, carry)
        self.assertEquals(3, register.word)

    def test_complement(self):
        register = Register(3)
        register.word = 5

        register.complement()
        self.assertEquals(2, register.word)

    def test_shift_right(self):
        register = Register(3)

        register.word = 5
        lsb = register.shift_right(0)
        self.assertEquals(1, lsb)
        self.assertEquals(2, register.word)

        register.word = 2
        lsb = register.shift_right(1)
        self.assertEquals(0, lsb)
        self.assertEquals(5, register.word)

    def test_shift_left(self):
        register = Register(3)

        register.word = 3
        msb = register.shift_left(0)
        self.assertEquals(0, msb)
        self.assertEquals(6, register.word)

        msb = register.shift_left(1)
        self.assertEquals(1, msb)
        self.assertEquals(5, register.word)


class TestMemory(TestCase):
    def test_read_write(self):
        memory = Memory(1024 * 4)
        memory.write(0x000, 0x000A)
        memory.write(0x001, 0x000B)
        memory.write(0x002, 0x000C)
        self.assertEquals(0x000A, memory.read(0x000))
        self.assertEquals(0x000B, memory.read(0x001))
        self.assertEquals(0x000C, memory.read(0x002))


class TestComputer(TestCase):
    def test_simple_program(self):
        computer = Computer()

        program = """
            ORG 100
            CLA
            INC
            HLT
            END
        """
        assembler = Assembler(program)
        assembler.load(computer.ram)

        computer.run(0x100)

        self.assertEquals(1, computer.ac.word)

    def test_add_two_numbers(self):
        computer = Computer()

        program = """
                 ORG 100
                 LDA AAA
                 ADD BBB
                 STA CCC
                 HLT
            AAA, DEC 83
            BBB, DEC -23
            CCC, HEX 0
                 END
        """
        assembler = Assembler(program)
        assembler.load(computer.ram)

        computer.run(0x100)

        self.assertEquals(60, computer.ram.read(0x106))

    def test_subtract_two_numbers(self):
        computer = Computer()

        program = """
                 ORG 100
                 LDA BBB
                 CMA
                 INC
                 ADD AAA
                 STA CCC
                 HLT
            AAA, DEC 83
            BBB, DEC -23
            CCC, HEX 0
                 END
        """
        assembler = Assembler(program)
        assembler.load(computer.ram)

        computer.run(0x100)

        self.assertEquals(106, computer.ram.read(0x108))