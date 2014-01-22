from unittest import TestCase
from amitayh.mano.computer import Register, Memory


class TestRegister(TestCase):
    def test_increment(self):
        r = Register(3)
        r.word = 5

        r.inc()
        self.assertEquals(6, r.word)

        r.inc()
        self.assertEquals(7, r.word)

        r.inc()
        self.assertEquals(0, r.word)


class TestMemory(TestCase):
    def test_read_write(self):
        m = Memory(1024 * 4)
        m.write(0x000, 0x000A)
        m.write(0x001, 0x000B)
        m.write(0x002, 0x000C)
        self.assertEquals(0x000A, m.read(0x000))
        self.assertEquals(0x000B, m.read(0x001))
        self.assertEquals(0x000C, m.read(0x002))


class TestComputer(TestCase):
    def test_simple_program(self):
        pass



