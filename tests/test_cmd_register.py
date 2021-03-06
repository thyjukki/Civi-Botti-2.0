from unittest import TestCase
from unittest.mock import Mock, patch

from peewee import SqliteDatabase
from telegram.ext import ConversationHandler
from civbot import gmr

from civbot.commands import cmd_register
from civbot.models import database_proxy, User
from civbot.exceptions import InvalidAuthKey


class TestRegister(TestCase):
    def test_register_should_go_to_authkey(self):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User])

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 0

        self.assertEqual(cmd_register.AUTHKEY, cmd_register.register(bot_mock, update_mock))
        update_mock.message.reply_text.assert_called()

    def test_register_fails_if_registered(self):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User])

        User.create(id=111, steam_id=0, authorization_key='')

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 111

        self.assertEqual(ConversationHandler.END, cmd_register.register(bot_mock, update_mock))
        update_mock.message.reply_text.assert_called()

    @patch('civbot.gmr.get_steam_id_from_auth')
    def test_authkey_should_retry_if_fail(self, mock_gmr):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User])

        bot_mock = Mock()

        update_mock = Mock()
        update_mock.message.from_user.id = 232
        update_mock.message.text = 'auth_key'

        mock_gmr.side_effect = InvalidAuthKey

        self.assertEqual(cmd_register.AUTHKEY, cmd_register.authkey(bot_mock, update_mock))

        update_mock.message.reply_text.assert_called_with("Authkey incorrect, try again (/cancel to end)")
        mock_gmr.assert_called_with('auth_key')

        user = User.get_or_none(User.id == 232)
        self.assertIsNone(user)

    @patch('civbot.gmr.get_steam_id_from_auth', return_value=123123)
    def test_authkey_should_success_and_create_user(self, mock_gmr):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User])

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 111
        update_mock.message.text = 'auth_key'

        self.assertEqual(ConversationHandler.END, cmd_register.authkey(bot_mock, update_mock))

        update_mock.message.reply_text.assert_called_with("Successfully registered with steam id 123123")
        mock_gmr.assert_called_with('auth_key')

        user = User.get_or_none(User.id == 111)
        self.assertIsNotNone(user)
        self.assertEqual(123123, user.steam_id)
        self.assertEqual('auth_key', user.authorization_key)
