from unittest import TestCase
from amitayh.mano.assembler import Assembler
from amitayh.mano.computer import Register, Memory, Computer


class TestComputer(TestCase):
    def test_simple_program(self):
        program = """
            ORG 100
            CLA
            INC
            HLT
            END
        """
        computer = self.create_computer(program)

        self.assertEquals(1, computer.ac.word)

    def test_add_two_numbers(self):
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
        computer = self.create_computer(program)

        self.assertEquals(60, computer.ram.read(0x106))

    def test_subtract_two_numbers(self):
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
        computer = self.create_computer(program)

        self.assertEquals(106, computer.ram.read(0x108))

    def test_add_16_numbers(self):
        program = """
                 ORG 100
                 CLA
            LOP, ADD PTR I
                 ISZ PTR
                 ISZ CNT
                 BUN LOP
                 STA SUM
                 HLT
            SUM, HEX 0
            PTR, HEX 200
            CNT, DEC -16

                 ORG 200
                 HEX 10
                 HEX 20
                 HEX 30
                 HEX 40
                 HEX 50
                 HEX 60
                 HEX 70
                 HEX 80
                 HEX 90
                 HEX A0
                 HEX B0
                 HEX C0
                 HEX D0
                 HEX E0
                 HEX F0
                 HEX 100
                 END
        """
        computer = self.create_computer(program)

        # 0x10 + 0x20 + ... + 0x100 = 0x880
        self.assertEquals(0x880, computer.ram.read(0x107))

    def test_call_function(self):
        program = """
                  ORG 10
                  BSA FUNC
                  DEC 5
                  HEX 40
            SUM,  HEX 0
                  LDA SUM
                  HLT

            PTR,  HEX 0
            CNT,  HEX 0
            FUNC, HEX 0
                  LDA FUNC I
                  CMA
                  INC
                  STA CNT
                  ISZ FUNC
                  LDA FUNC I
                  STA PTR
                  CLA
            LOOP, ADD PTR I
                  ISZ PTR
                  ISZ CNT
                  BUN LOOP
                  ISZ FUNC
                  STA FUNC I
                  ISZ FUNC
                  BUN FUNC I

                  ORG 40
            DATA, DEC 1
                  DEC 2
                  DEC 4
                  DEC 8
                  DEC 16
                  DEC 32
                  DEC 64
                  DEC 128
                  DEC 256
                  DEC 512
                  DEC 1024
                  END
        """
        computer = self.create_computer(program)

        # 1 + 2 + 4 + 8 + 16 = 31
        self.assertEquals(31, computer.ac.word)

    @staticmethod
    def create_computer(program):
        computer = Computer()
        assembler = Assembler(program)
        program_start = assembler.load(computer.ram)
        computer.run(program_start)

        return computer

class TestRegister(TestCase):
    def setUp(self):
        self.register = Register(3)
        self.register.word = 5

    def tearDown(self):
        self.register = None

    def test_increment(self):
        self.register.increment()
        self.assertEquals(6, self.register.word)

        self.register.increment()
        self.assertEquals(7, self.register.word)

        self.register.increment()
        self.assertEquals(0, self.register.word)

    def test_clear(self):
        self.register.clear()
        self.assertEquals(0, self.register.word)

    def test_logic_and(self):
        self.register.logic_and(6)
        self.assertEquals(5 & 6, self.register.word)

    def test_add(self):
        carry = self.register.add(6)
        self.assertEquals(1, carry)
        self.assertEquals(3, self.register.word)

    def test_complement(self):
        self.register.complement()
        self.assertEquals(2, self.register.word)

    def test_shift_right(self):
        lsb = self.register.shift_right(0)
        self.assertEquals(1, lsb)
        self.assertEquals(2, self.register.word)

        self.register.word = 2
        lsb = self.register.shift_right(1)
        self.assertEquals(0, lsb)
        self.assertEquals(5, self.register.word)

    def test_shift_left(self):
        self.register.word = 3
        msb = self.register.shift_left(0)
        self.assertEquals(0, msb)
        self.assertEquals(6, self.register.word)

        msb = self.register.shift_left(1)
        self.assertEquals(1, msb)
        self.assertEquals(5, self.register.word)


class TestMemory(TestCase):
    def setUp(self):
        self.memory = Memory(1024 * 4)

    def tearDown(self):
        self.memory = None

    def test_read_write(self):
        self.memory.write(0x000, 0x000A)
        self.memory.write(0x001, 0x000B)
        self.memory.write(0x002, 0x000C)
        self.assertEquals(0x000A, self.memory.read(0x000))
        self.assertEquals(0x000B, self.memory.read(0x001))
        self.assertEquals(0x000C, self.memory.read(0x002))