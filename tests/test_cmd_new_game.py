import json
from unittest import TestCase
from unittest.mock import patch, Mock

from peewee import SqliteDatabase
from telegram.ext import ConversationHandler

from civbot.commands import cmd_new_game
from civbot.models import database_proxy, User, Game


class TestAddGame(TestCase):
    def test_add_game_should_fail_if_not_registered(self):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User])

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 0

        self.assertEqual(ConversationHandler.END, cmd_new_game.new_game(bot_mock, update_mock))
        update_mock.message.reply_text.assert_called_with('You are not registered!')

    @patch('civbot.gmr.get_games')
    def test_add_game_should_display_error_if_no_games_fetched(self, get_games_mock):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game])
        User.create(id=111, steam_id='', authorization_key='')

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 111

        get_games_mock.return_value = []

        self.assertEqual(ConversationHandler.END, cmd_new_game.new_game(bot_mock, update_mock))
        update_mock.message.reply_text.assert_called_with('You are not part of any games')

    @patch('civbot.gmr.get_games')
    def test_add_game_should_display_error_if_no_available_games(self, get_games_mock):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game])
        mock_user = User.create(id=111, steam_id='', authorization_key='')
        Game.create(id=27532, owner=mock_user, name='test game')

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 111

        json_data = json.load(open('./fixtures/game_request.json'))

        game_data = json_data['Games']
        get_games_mock.return_value = game_data

        self.assertEqual(ConversationHandler.END, cmd_new_game.new_game(bot_mock, update_mock))
        update_mock.message.reply_text.assert_called_with('No games to be added')

    @patch('telegram.ReplyKeyboardMarkup')
    @patch('civbot.gmr.get_games')
    def test_new_game_should_return_list_of_games(self, get_games_mock, mock_keyboard):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game])
        User.create(id=111, steam_id='', authorization_key='')

        mock_keyboard.return_value = mock_keyboard
        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 111

        json_data = json.load(open('./fixtures/game_request.json'))

        game_data = json_data['Games']
        get_games_mock.return_value = game_data

        self.assertEqual(cmd_new_game.SELECT, cmd_new_game.new_game(bot_mock, update_mock))
        update_mock.message.reply_text.assert_called_with('Chose the game', reply_markup=mock_keyboard)
        mock_keyboard.assert_called()

    @patch('telegram.ReplyKeyboardRemove')
    def test_select_game_should_cancel_and_clear_keyboard(self, mock_keyboard):
        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.text = 'cancel'
        mock_keyboard.return_value = mock_keyboard

        self.assertEqual(ConversationHandler.END, cmd_new_game.select_game(bot_mock, update_mock))
        update_mock.message.reply_text.assert_called_with('Canceled', reply_markup=mock_keyboard)

    @patch('telegram.ReplyKeyboardRemove')
    @patch('civbot.gmr.get_games')
    def test_select_game_should_fail_if_game_does_not_exist(self, get_games_mock, mock_keyboard):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User])
        User.create(id=111, steam_id='', authorization_key='')

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 111
        update_mock.message.text = 'game'
        mock_keyboard.return_value = mock_keyboard

        json_data = json.load(open('./fixtures/game_request.json'))

        game_data = json_data['Games']
        get_games_mock.return_value = game_data

        self.assertEqual(ConversationHandler.END, cmd_new_game.select_game(bot_mock, update_mock))
        update_mock.message.reply_text.assert_called_with('Game does not exist', reply_markup=mock_keyboard)

    @patch('telegram.ReplyKeyboardRemove')
    @patch('civbot.gmr.get_games')
    def test_select_game_should_fail_if_game_had_been_registered(self, get_games_mock, mock_keyboard):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game])
        mock_user = User.create(id=111, steam_id='', authorization_key='')
        Game.create(id=27532, owner=mock_user, name='Tietokilta Top Dictator 3.0')

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 111
        update_mock.message.text = 'Tietokilta Top Dictator 3.0'
        mock_keyboard.return_value = mock_keyboard

        json_data = json.load(open('./fixtures/game_request.json'))

        game_data = json_data['Games']
        get_games_mock.return_value = game_data

        self.assertEqual(ConversationHandler.END, cmd_new_game.select_game(bot_mock, update_mock))
        update_mock.message.reply_text.assert_called_with('Game already registered', reply_markup=mock_keyboard)

    @patch('telegram.ReplyKeyboardRemove')
    @patch('civbot.gmr.get_games')
    def test_select_game_should_create_new_game_object(self, get_games_mock, mock_keyboard):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game])
        mock_user = User.create(id=111, steam_id='', authorization_key='')

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 111
        update_mock.message.text = 'Tietokilta Top Dictator 3.0'
        mock_keyboard.return_value = mock_keyboard

        json_data = json.load(open('./fixtures/game_request.json'))

        game_data = json_data['Games']
        get_games_mock.return_value = game_data

        self.assertEqual(ConversationHandler.END, cmd_new_game.select_game(bot_mock, update_mock))
        update_mock.message.reply_text.assert_called_with(
            'Game Tietokilta Top Dictator 3.0 registered',
            reply_markup=mock_keyboard
        )

        game = Game.get_or_none(Game.id == 27532)
        self.assertIsNotNone(game)
        self.assertEqual(mock_user, game.owner)
        self.assertEqual('Tietokilta Top Dictator 3.0', game.name)
