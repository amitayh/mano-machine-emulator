from unittest import TestCase
from amitayh.mano.assembler import Assembler
from amitayh.mano.computer import Memory


class TestAssembler(TestCase):
    def setUp(self):
        self.memory = Memory(1024 * 4)

    def tearDown(self):
        self.memory = None

    def test_assemble_rri_commands(self):
        program = """
            ORG 0
            CLA
            CLE
            CMA
            CME
            CIR
            CIL
            INC
            SPA
            SNA
            SZA
            SZE
            HLT
            END
        """
        program_start = self.load_program(program)

        self.assertEquals(0, program_start)
        self.assertEquals(0x7800, self.memory.read(0x0))
        self.assertEquals(0x7400, self.memory.read(0x1))
        self.assertEquals(0x7200, self.memory.read(0x2))
        self.assertEquals(0x7100, self.memory.read(0x3))
        self.assertEquals(0x7080, self.memory.read(0x4))
        self.assertEquals(0x7040, self.memory.read(0x5))
        self.assertEquals(0x7020, self.memory.read(0x6))
        self.assertEquals(0x7010, self.memory.read(0x7))
        self.assertEquals(0x7008, self.memory.read(0x8))
        self.assertEquals(0x7004, self.memory.read(0x9))
        self.assertEquals(0x7002, self.memory.read(0xA))
        self.assertEquals(0x7001, self.memory.read(0xB))

    def test_assemble_io_commands(self):
        program = """
            ORG 100
            INP
            OUT
            SKI
            SKO
            ION
            IOF
            END
        """
        program_start = self.load_program(program)

        self.assertEquals(0x100, program_start)
        self.assertEquals(0xF800, self.memory.read(0x100))
        self.assertEquals(0xF400, self.memory.read(0x101))
        self.assertEquals(0xF200, self.memory.read(0x102))
        self.assertEquals(0xF100, self.memory.read(0x103))
        self.assertEquals(0xF080, self.memory.read(0x104))
        self.assertEquals(0xF040, self.memory.read(0x105))

    def test_assemble_mri_commands(self):
        program = """
                 ORG 100
                 AND AAA
                 AND AAA I
                 ADD BBB
                 ADD BBB I
                 LDA CCC
                 LDA CCC I
                 STA DDD
                 STA DDD I
                 BUN EEE
                 BUN EEE I
                 BSA FFF
                 BSA FFF I
                 ISZ GGG
                 ISZ GGG I
            AAA, HEX 0
            BBB, HEX 1
            CCC, HEX 2
            DDD, HEX 4
            EEE, HEX 8
            FFF, HEX F
            GGG, DEC -23
                 END
        """
        program_start = self.load_program(program)

        self.assertEquals(0x100, program_start)
        self.assertEquals(0x010E, self.memory.read(0x100))
        self.assertEquals(0x810E, self.memory.read(0x101))
        self.assertEquals(0x110F, self.memory.read(0x102))
        self.assertEquals(0x910F, self.memory.read(0x103))
        self.assertEquals(0x2110, self.memory.read(0x104))
        self.assertEquals(0xA110, self.memory.read(0x105))
        self.assertEquals(0x3111, self.memory.read(0x106))
        self.assertEquals(0xB111, self.memory.read(0x107))
        self.assertEquals(0x4112, self.memory.read(0x108))
        self.assertEquals(0xC112, self.memory.read(0x109))
        self.assertEquals(0x5113, self.memory.read(0x10A))
        self.assertEquals(0xD113, self.memory.read(0x10B))
        self.assertEquals(0x6114, self.memory.read(0x10C))
        self.assertEquals(0xE114, self.memory.read(0x10D))

        self.assertEquals(0x0, self.memory.read(0x10E))
        self.assertEquals(0x1, self.memory.read(0x10F))
        self.assertEquals(0x2, self.memory.read(0x110))
        self.assertEquals(0x4, self.memory.read(0x111))
        self.assertEquals(0x8, self.memory.read(0x112))
        self.assertEquals(0xF, self.memory.read(0x113))
        self.assertEquals(-23, self.memory.read(0x114))

    def test_invalid_command_throws_error(self):
        program = """
            ORG 100
            FOO
            END
        """
        assembler = Assembler(program)
        self.assertRaises(SyntaxError, assembler.load, self.memory)

    def load_program(self, program):
        assembler = Assembler(program)
        return assembler.load(self.memory)