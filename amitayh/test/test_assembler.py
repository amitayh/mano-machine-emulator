from unittest import TestCase
from amitayh.mano.assembler import Assembler
from amitayh.mano.computer import Memory


class TestAssembler(TestCase):
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
        memory = Memory(1024 * 4)

        assembler = Assembler(program)
        program_start = assembler.load(memory)

        self.assertEquals(0, program_start)
        self.assertEquals(0x7800, memory.read(0x0))
        self.assertEquals(0x7400, memory.read(0x1))
        self.assertEquals(0x7200, memory.read(0x2))
        self.assertEquals(0x7100, memory.read(0x3))
        self.assertEquals(0x7080, memory.read(0x4))
        self.assertEquals(0x7040, memory.read(0x5))
        self.assertEquals(0x7020, memory.read(0x6))
        self.assertEquals(0x7010, memory.read(0x7))
        self.assertEquals(0x7008, memory.read(0x8))
        self.assertEquals(0x7004, memory.read(0x9))
        self.assertEquals(0x7002, memory.read(0xA))
        self.assertEquals(0x7001, memory.read(0xB))

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
        memory = Memory(1024 * 4)

        assembler = Assembler(program)
        program_start = assembler.load(memory)

        self.assertEquals(0x100, program_start)
        self.assertEquals(0xF800, memory.read(0x100))
        self.assertEquals(0xF400, memory.read(0x101))
        self.assertEquals(0xF200, memory.read(0x102))
        self.assertEquals(0xF100, memory.read(0x103))
        self.assertEquals(0xF080, memory.read(0x104))
        self.assertEquals(0xF040, memory.read(0x105))

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
        memory = Memory(1024 * 4)

        assembler = Assembler(program)
        program_start = assembler.load(memory)

        self.assertEquals(0x100, program_start)
        self.assertEquals(0x010E, memory.read(0x100))
        self.assertEquals(0x810E, memory.read(0x101))
        self.assertEquals(0x110F, memory.read(0x102))
        self.assertEquals(0x910F, memory.read(0x103))
        self.assertEquals(0x2110, memory.read(0x104))
        self.assertEquals(0xA110, memory.read(0x105))
        self.assertEquals(0x3111, memory.read(0x106))
        self.assertEquals(0xB111, memory.read(0x107))
        self.assertEquals(0x4112, memory.read(0x108))
        self.assertEquals(0xC112, memory.read(0x109))
        self.assertEquals(0x5113, memory.read(0x10A))
        self.assertEquals(0xD113, memory.read(0x10B))
        self.assertEquals(0x6114, memory.read(0x10C))
        self.assertEquals(0xE114, memory.read(0x10D))

        self.assertEquals(0x0, memory.read(0x10E))
        self.assertEquals(0x1, memory.read(0x10F))
        self.assertEquals(0x2, memory.read(0x110))
        self.assertEquals(0x4, memory.read(0x111))
        self.assertEquals(0x8, memory.read(0x112))
        self.assertEquals(0xF, memory.read(0x113))
        self.assertEquals(-23, memory.read(0x114))

    def test_invalid_command_throws_error(self):
        program = """
            ORG 100
            FOO
            END
        """
        memory = Memory(1024 * 4)

        assembler = Assembler(program)
        self.assertRaises(SyntaxError, assembler.load, memory)