from unittest import TestCase
from amitayh.mano.logger import Logger


class TestLogger(TestCase):
    def setUp(self):
        self.logger = Logger()

    def tearDown(self):
        self.logger = None

    def test_log_should_be_empty_on_init(self):
        self.assertEquals([], self.logger.messages)

    def test_log_messages_should_enter_a_list(self):
        self.logger.log('foo')
        self.logger.log('bar')
        self.logger.log('baz')
        self.assertEquals(['foo', 'bar', 'baz'], self.logger.messages)

    def test_string_representation(self):
        self.assertEquals('Logger()', str(self.logger))

        self.logger.log('foo')
        self.assertEquals('Logger(last_message="foo")', str(self.logger))

        self.logger.log('bar')
        self.assertEquals('Logger(last_message="bar")', str(self.logger))