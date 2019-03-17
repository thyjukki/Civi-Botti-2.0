from unittest import TestCase
from unittest.mock import patch, Mock

from peewee import SqliteDatabase
from telegram.ext import ConversationHandler

from civbot.commands import cmd_add_game
from civbot.models import database_proxy, User, Game, Subscription


class TestAddGame(TestCase):
    def test_add_game_should_fail_if_not_registered(self):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User])

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 0

        self.assertEqual(ConversationHandler.END, cmd_add_game.add_game(bot_mock, update_mock))
        update_mock.message.reply_text.assert_called_with('You are not registered!')

    def test_add_game_should_fail_if_not_admin_of_group(self):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User])
        User.create(id=111, steam_id='', authorization_key='')

        admin_mock = Mock()
        admin_mock.user.id = 23
        bot_mock = Mock()
        bot_mock.get_chat_administrators.return_value = [admin_mock]
        update_mock = Mock()
        update_mock.message.from_user.id = 111

        self.assertEqual(ConversationHandler.END, cmd_add_game.add_game(bot_mock, update_mock))
        update_mock.message.reply_text.assert_called_with('You are not admin of the group!')

    def test_add_game_should_display_error_if_no_registered_games(self):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game])
        User.create(id=111, steam_id='', authorization_key='')

        admin_mock = Mock()
        admin_mock.user.id = 111
        bot_mock = Mock()
        bot_mock.get_chat_administrators.return_value = [admin_mock]
        update_mock = Mock()
        update_mock.message.from_user.id = 111

        self.assertEqual(ConversationHandler.END, cmd_add_game.add_game(bot_mock, update_mock))
        update_mock.message.reply_text.assert_called_with("You don't have any registered games")

    def test_add_game_should_display_error_if_no_only_registered_game_is_added(self):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game, Subscription])
        user_mock = User.create(id=111, steam_id='', authorization_key='')
        game_mock = Game.create(id=1, owner=user_mock, name='test game')
        Subscription.create(game=game_mock, chat_id=1234)

        admin_mock = Mock()
        admin_mock.user.id = 111
        bot_mock = Mock()
        bot_mock.get_chat_administrators.return_value = [admin_mock]
        update_mock = Mock()
        update_mock.message.from_user.id = 111
        update_mock.message.chat_id = 1234

        self.assertEqual(ConversationHandler.END, cmd_add_game.add_game(bot_mock, update_mock))
        update_mock.message.reply_text.assert_called_with("You don't have any registered games not in this chat")

    @patch('telegram.ReplyKeyboardMarkup')
    def test_add_game_should_display_list_of_games(self, mock_keyboard):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game, Subscription])
        user_mock = User.create(id=111, steam_id='', authorization_key='')
        Game.create(id=1, owner=user_mock, name='test game')

        mock_keyboard.return_value = mock_keyboard
        admin_mock = Mock()
        admin_mock.user.id = 111
        bot_mock = Mock()
        bot_mock.get_chat_administrators.return_value = [admin_mock]
        update_mock = Mock()
        update_mock.message.from_user.id = 111
        update_mock.message.chat_id = 1234

        self.assertEqual(cmd_add_game.SELECT, cmd_add_game.add_game(bot_mock, update_mock))
        update_mock.message.reply_text.assert_called_with('Chose the game', reply_markup=mock_keyboard)
        mock_keyboard.assert_called()

    @patch('telegram.ReplyKeyboardRemove')
    def test_select_should_fail_if_wrong_game(self, mock_keyboard):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game, Subscription])
        user_mock = User.create(id=111, steam_id='', authorization_key='')
        Game.create(id=1, owner=user_mock, name='test game')

        mock_keyboard.return_value = mock_keyboard
        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 111
        update_mock.message.text = 'failed game'

        self.assertEqual(ConversationHandler.END, cmd_add_game.select_game(bot_mock, update_mock))
        update_mock.message.reply_text.assert_called_with('Game does not exist', reply_markup=mock_keyboard)

    @patch('telegram.ReplyKeyboardRemove')
    def test_select_should_fail_if_game_was_added(self, mock_keyboard):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game, Subscription])
        user_mock = User.create(id=111, steam_id='', authorization_key='')
        game_mock = Game.create(id=1, owner=user_mock, name='test game')
        Subscription.create(game=game_mock, chat_id=1234)

        mock_keyboard.return_value = mock_keyboard
        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 111
        update_mock.message.chat_id = 1234
        update_mock.message.text = game_mock.name

        self.assertEqual(ConversationHandler.END, cmd_add_game.select_game(bot_mock, update_mock))
        update_mock.message.reply_text.assert_called_with('Game has already been added', reply_markup=mock_keyboard)

    @patch('telegram.ReplyKeyboardRemove')
    def test_select_should_display_canceled_if_canceled(self, mock_keyboard):
        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.text = 'cancel'
        mock_keyboard.return_value = mock_keyboard

        self.assertEqual(ConversationHandler.END, cmd_add_game.select_game(bot_mock, update_mock))
        update_mock.message.reply_text.assert_called_with('Canceled', reply_markup=mock_keyboard)

    @patch('telegram.ReplyKeyboardRemove')
    def test_select_should_add_the_game_to_group(self, mock_keyboard):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game, Subscription])
        user_mock = User.create(id=111, steam_id='', authorization_key='')
        game_mock = Game.create(id=1, owner=user_mock, name='test game')

        mock_keyboard.return_value = mock_keyboard
        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 111
        update_mock.message.chat_id = 1234
        update_mock.message.text = game_mock.name

        self.assertEqual(ConversationHandler.END, cmd_add_game.select_game(bot_mock, update_mock))
        update_mock.message.reply_text.assert_called_with(
            f'Subscribed to {game_mock.name}. This chat will now start receiving notifications for the '
            'game. To get notifications, send /register to me as private message',
            reply_markup=mock_keyboard)
        sub = Subscription.get_or_none(Subscription.game == game_mock, Subscription.chat_id == 1234)
        self.assertIsNotNone(sub)
