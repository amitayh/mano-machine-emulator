from unittest import TestCase
from amitayh.mano.logger import Logger


class TestLogger(TestCase):
    def test_log_should_be_empty_on_init(self):
        logger = Logger()
        self.assertEquals([], logger.messages)

    def test_log_messages_should_enter_a_list(self):
        logger = Logger()
        logger.log('foo')
        logger.log('bar')
        logger.log('baz')
        self.assertEquals(['foo', 'bar', 'baz'], logger.messages)