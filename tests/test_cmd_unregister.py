from unittest import TestCase
from unittest.mock import Mock, patch

from peewee import SqliteDatabase
from telegram.ext import ConversationHandler

from civbot.commands import cmd_unregister
from civbot.models import database_proxy, User


class TestUnregister(TestCase):
    @patch('telegram.ReplyKeyboardMarkup')
    def test_unregister_should_go_to_verify(self, mock_keyboard):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User])
        User.create(id=111, steam_id='', authorization_key='')

        mock_keyboard.return_value = mock_keyboard
        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 111

        self.assertEqual(cmd_unregister.VERIFY, cmd_unregister.unregister(bot_mock, update_mock))
        bot_mock.send_message.assert_called_with(
            chat_id=update_mock.message.chat_id,
            text="Are you sure you want to register."
                 "You will stop receiving notifications from current games."
                 "Your steam id is still kept in order for active games to function."
                 "You can register back anytime to continue receiving notifications.",
            reply_markup=mock_keyboard
        )
        mock_keyboard.assert_called()

    def test_register_fails_if_not_registered(self):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User])

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 111

        self.assertEqual(ConversationHandler.END, cmd_unregister.unregister(bot_mock, update_mock))
        bot_mock.send_message.assert_called_with(
            chat_id=update_mock.message.chat_id,
            text="You are not registered!")

    @patch('telegram.ReplyKeyboardRemove')
    def test_verify_should_cancel_if_no(self, mock_keyboard):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User])
        User.create(id=111, steam_id='', authorization_key='')

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 111
        update_mock.message.text = 'No'
        mock_keyboard.return_value = mock_keyboard

        self.assertEqual(ConversationHandler.END, cmd_unregister.unregister(bot_mock, update_mock))
        bot_mock.send_message.assert_called_with(
            chat_id=update_mock.message.chat_id,
            text="Canceling unregistering, your data was not removed!",
            reply_markup=mock_keyboard
        )
        self.assertIsNotNone(User.get_or_none(User.id == 111))

    @patch('telegram.ReplyKeyboardRemove')
    def test_verify_should_remove_user_if_yes(self, mock_keyboard):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User])
        User.create(id=111, steam_id='', authorization_key='')

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 111
        update_mock.message.text = 'Yes'
        mock_keyboard.return_value = mock_keyboard

        self.assertEqual(ConversationHandler.END, cmd_unregister.unregister(bot_mock, update_mock))
        bot_mock.send_message.assert_called_with(
            chat_id=update_mock.message.chat_id,
            text="Unregistered, your user data was removed!",
            reply_markup=mock_keyboard
        )
        self.assertIsNone(User.get_or_none(User.id == 111))

