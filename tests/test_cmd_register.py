from unittest import TestCase
from unittest.mock import Mock, patch

from peewee import SqliteDatabase
from telegram.ext import ConversationHandler

from civbot.commands import cmd_register
from civbot.models import database_proxy, User


class TestRegister(TestCase):
    def test_register_should_go_to_authkey(self):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User])
        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 0

        self.assertEqual(cmd_register.AUTHKEY, cmd_register.register(bot_mock, update_mock))
        bot_mock.send_message.assert_called()

    def test_register_fails_if_registered(self):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User])

        User.create(id=111, steam_id='', authorization_key='')

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 111

        self.assertEqual(ConversationHandler.END, cmd_register.register(bot_mock, update_mock))

    @patch('gmr.get_steam_id_from_auth', return_value='null')
    def test_authkey_should_retry_if_fail(self, mock_gmr):
        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 0

        self.assertEqual(cmd_register.AUTHKEY, cmd_register.authkey(bot_mock, update_mock))
        bot_mock.send_message.assert_called()

    @patch('gmr.get_steam_id_from_auth', return_value='steamid')
    def test_authkey_should_retry_proper(self, mock_gmr):
        bot_mock = Mock()
        update_mock = Mock()

        self.assertEqual(ConversationHandler.END, cmd_register.authkey(bot_mock, update_mock))
        bot_mock.send_message.assert_called()
