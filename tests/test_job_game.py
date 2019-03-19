import json
import os
from unittest import TestCase
from unittest.mock import Mock, patch

from peewee import SqliteDatabase

from civbot.exceptions import GameNoLongerExist
from civbot.jobs import job_games
from civbot.models import Game, database_proxy, User, Subscription


class TestGameJob(TestCase):
    @patch('civbot.gmr.get_game_data')
    def test_poll_game_should_fail_and_deactivate_game_if_it_no_longer_exists(
            self,
            mock_gmr
    ):
        bot_mock = Mock()
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game])

        user = User.create(id=111, steam_id=0, authorization_key='')
        game = Game.create(
            id=27532,
            name='Tietokilta Top Dictator 3.0',
            owner=user
        )

        mock_gmr.side_effect = GameNoLongerExist

        self.assertEqual(False, job_games.poll_game(bot_mock, game))
        game.refresh()
        self.assertEqual(False, game.active)

    @patch('civbot.gmr.get_game_data')
    def test_poll_game_should_return_false_if_it_is_not_in_any_chats(
            self,
            mock_gmr
    ):
        bot_mock = Mock()
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game, Subscription])

        with open((os.path.dirname(__file__))
                  + '/fixtures/game_request.json') as f:
            json_data = json.load(f)

        mock_gmr.return_value = json_data['Games'][0]

        user = User.create(id=111, steam_id=0, authorization_key='')
        game = Game.create(
            id=27532,
            name='Tietokilta Top Dictator 3.0',
            owner=user
        )

        self.assertEqual(False, job_games.poll_game(bot_mock, game))
        game.refresh()
        self.assertEqual(True, game.active)

    @patch('civbot.gmr.get_game_data')
    def test_poll_game_should_return_false_if_nothing_has_changed(
            self,
            mock_gmr
    ):
        bot_mock = Mock()
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game, Subscription])

        user = User.create(id=111, steam_id=0, authorization_key='')
        game = Game.create(
            id=27532,
            name='Tietokilta Top Dictator 3.0',
            owner=user,
            current_steam_id=76561198002501851
        )
        Subscription.create(game=game, chat_id=1234)

        with open((os.path.dirname(__file__))
                  + '/fixtures/game_request.json') as f:
            json_data = json.load(f)

        mock_gmr.return_value = json_data['Games'][0]

        self.assertEqual(False, job_games.poll_game(bot_mock, game))
        game.refresh()
        self.assertEqual(True, game.active)

    @patch('civbot.gmr.get_game_data')
    def test_poll_game_should_return_true_and_ping_chat_if_turn_has_changed(
            self,
            mock_gmr
    ):
        bot_mock = Mock()
        bot_mock.get_chat.return_value.username = 'test_user'
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game, Subscription])

        user = User.create(
            id=111,
            steam_id=76561198002501851,
            authorization_key=''
        )
        game = Game.create(
            id=27532,
            name='Tietokilta Top Dictator 3.0',
            owner=user,
            current_steam_id=76561198036077154
        )
        Subscription.create(game=game, chat_id=1234)

        with open((os.path.dirname(__file__))
                  + '/fixtures/game_request.json') as f:
            json_data = json.load(f)

        mock_gmr.return_value = json_data['Games'][0]

        self.assertEqual(True, job_games.poll_game(bot_mock, game))
        game.refresh()
        self.assertEqual(True, game.active)
        self.assertEqual(76561198002501851, game.current_steam_id)
        bot_mock.send_message.assert_called_with(
            chat_id=1234,
            text="It's now your turn @test_user"
        )
        bot_mock.get_chat.assert_called()

    @patch('steamwebapi.profiles.get_user_profile')
    @patch('civbot.gmr.get_game_data')
    def test_poll_game_should_return_true_and_ping_chat_using_steam_name(
            self,
            mock_gmr,
            mock_steam
    ):
        bot_mock = Mock()
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game, Subscription])

        user = User.create(id=111, steam_id=0, authorization_key='')
        game = Game.create(
            id=27532,
            name='Tietokilta Top Dictator 3.0',
            owner=user,
            current_steam_id=76561198036077154
        )
        Subscription.create(game=game, chat_id=1234)

        with open((os.path.dirname(__file__))
                  + '/fixtures/game_request.json') as f:
            json_data = json.load(f)

        mock_gmr.return_value = json_data['Games'][0]
        mock_steam.return_value.personaname = 'steam_name'

        self.assertEqual(True, job_games.poll_game(bot_mock, game))
        game.refresh()
        self.assertEqual(True, game.active)
        self.assertEqual(76561198002501851, game.current_steam_id)
        bot_mock.send_message.assert_called_with(
            chat_id=1234,
            text="It's now your turn steam_name"
        )
