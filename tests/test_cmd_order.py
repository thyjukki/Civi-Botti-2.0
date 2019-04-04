import json
import os
from unittest import TestCase
from unittest.mock import Mock, patch

from peewee import SqliteDatabase

from civbot.commands import cmd_order
from civbot.models import database_proxy, User, Subscription, Game, Player


class TestOrder(TestCase):
    def test_order_should_fail_if_no_games_in_chat(self):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game, Subscription])

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 0
        update_mock.message.chat_id = 101

        cmd_order.order(bot_mock, update_mock)
        update_mock.message.reply_text.assert_called_with(
            'No games added to this chat'
        )

    @patch('civbot.gmr.get_games')
    def test_order_should_fail_if_game_is_not_active(
        self,
        get_games_mock
    ):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game, Subscription])

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 0
        update_mock.message.chat_id = 1234

        user_mock = User.create(id=111, steam_id=0, authorization_key='')
        game_mock = Game.create(
            id=1,
            owner=user_mock,
            name='test game',
            active=False
        )
        Subscription.create(game=game_mock, chat_id=1234)

        cmd_order.order(bot_mock, update_mock)
        update_mock.message.reply_text.assert_called_with(
            'Game is over'
        )
        get_games_mock.assert_not_called()

    @patch('civbot.gmr.get_games')
    def test_order_should_fail_if_game_does_not_exist_anymore(
        self,
        get_games_mock
    ):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game, Subscription])

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 0
        update_mock.message.chat_id = 1234

        get_games_mock.return_value = []

        user_mock = User.create(id=111, steam_id=0, authorization_key='')
        game_mock = Game.create(id=1, owner=user_mock, name='test game')
        Subscription.create(game=game_mock, chat_id=1234)

        cmd_order.order(bot_mock, update_mock)
        update_mock.message.reply_text.assert_called_with(
            'Game is over'
        )

    @staticmethod
    def get_name_from_steam_id(steam_id):
        name = {
            '76561190000000001': 'Player1',
            '76561190000000002': 'Player2',
            '76561190000000003': 'Player3',
            '76561190000000004': 'Player4',
            '76561190000000005': 'Player5',
            '76561190000000006': 'Player6',
            '76561190000000007': 'Player7',
            '76561190000000008': 'Player8',
        }[steam_id]

        mock_profile = Mock()
        mock_profile.personaname = name
        return mock_profile

    @patch(
        'steamwebapi.profiles.get_user_profile'''
    )
    @patch('civbot.gmr.get_games')
    def test_order_should_display_order_of_players(
        self,
        get_games_mock,
        mock_get_user_profile
    ):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game, Player, Subscription])

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 0
        update_mock.message.chat_id = 1234
        Player.insert_many(
            [
                {'steam_id': 76561190000000007, 'game_id': 27000, 'order': 6},
                {'steam_id': 76561190000000003, 'game_id': 27000, 'order': 2},
                {'steam_id': 76561190000000005, 'game_id': 27000, 'order': 4},
                {'steam_id': 76561190000000004, 'game_id': 27000, 'order': 3},
                {'steam_id': 76561190000000001, 'game_id': 27000, 'order': 0},
                {'steam_id': 76561190000000002, 'game_id': 27000, 'order': 1},
                {'steam_id': 76561190000000006, 'game_id': 27000, 'order': 5},
                {'steam_id': 76561190000000008, 'game_id': 27000, 'order': 7}
            ]
        ).execute()
        mock_get_user_profile.side_effect = self.get_name_from_steam_id

        with open((
            os.path.dirname(__file__))+'/fixtures/game_request.json'
        ) as f:
            json_data = json.load(f)

        game_data = json_data['Games']
        get_games_mock.return_value = game_data

        user_mock = User.create(
            id=111,
            steam_id=76561190000000000,
            authorization_key=''
        )
        game_mock = Game.create(id=27000, owner=user_mock, name='Test Game')
        Subscription.create(game=game_mock, chat_id=1234)

        cmd_order.order(bot_mock, update_mock)
        update_mock.message.reply_text.assert_called_with(
            'Order is:\n'
            'Player1\n'
            'Player2\n'
            'Player3\n'
            'Player4\n'
            'Player5\n'
            'Player6\n'
            'Player7\n'
            'Player8'
        )
