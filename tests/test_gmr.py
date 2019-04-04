import json
import os
from unittest import TestCase
from unittest.mock import patch

import requests_mock
from peewee import SqliteDatabase
from civbot.models import database_proxy, User, Game

from civbot import gmr
from civbot.exceptions import InvalidAuthKey, GameNoLongerExist


class TestGmr(TestCase):
    @requests_mock.Mocker()
    @patch('os.getenv', return_value='https://www.fake.com')
    def test_get_steam_id_from_auth(
        self,
        mock_request,
        mock_url
    ):
        steam_id = '76561190000000007'
        mock_request.get(
            "https://www.fake.com/api/Diplomacy/AuthenticateUser?authKey=key",
            text=steam_id
        )
        self.assertEqual(steam_id, gmr.get_steam_id_from_auth('key'))
        mock_url.assert_called_with('GMR_URL')

    def test_get_steam_id_from_auth_invalid(self):
        self.assertRaises(
            InvalidAuthKey,
            gmr.get_steam_id_from_auth,
            'null'
        )

    @requests_mock.Mocker()
    @patch('os.getenv', return_value='https://www.fake.com')
    def test_get_games_should_return_list_of_games(
            self,
            mock_request,
            mock_url
    ):
        with open(
            (os.path.dirname(__file__))+'/fixtures/game_request.json'
        ) as f:
            json_data = json.load(f)

        game_data = json_data['Games']

        mock_request.get(
            "https://www.fake.com/api/Diplomacy/GetGamesAndPlayers?p"
            "layerIDText=76561190000000007&authKey=test_auth_key",
            json=json_data
        )

        games = gmr.get_games(76561190000000007, 'test_auth_key')

        self.assertEqual(game_data, games)
        mock_url.assert_called_with('GMR_URL')

    @requests_mock.Mocker()
    @patch('os.getenv', return_value='https://www.fake.com')
    def test_get_game_data_should_return_data_for_selected_game(
            self,
            mock_request,
            mock_url
    ):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game])
        user_mock = User.create(
            id=111,
            steam_id=76561190000000007,
            authorization_key='test_auth_key'
        )
        game_mock = Game.create(id=27000, owner=user_mock, name='Test Game')
        with open(
            (os.path.dirname(__file__))+'/fixtures/game_request.json'
        ) as f:
            json_data = json.load(f)

        game_data = json_data['Games'][0]

        mock_request.get(
            "https://www.fake.com/api/Diplomacy/GetGamesAndPlayers?p"
            "layerIDText=76561190000000007&authKey=test_auth_key",
            json=json_data
        )

        games = gmr.get_game_data(game_mock)

        self.assertEqual(game_data, games)
        mock_url.assert_called_with('GMR_URL')

    @requests_mock.Mocker()
    @patch('os.getenv', return_value='https://www.fake.com')
    def test_get_game_data_should_raise_exception_if_game_does_not_exist(
            self,
            mock_request,
            mock_url
    ):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game])
        user_mock = User.create(
            id=111,
            steam_id=76561190000000007,
            authorization_key='test_auth_key'
        )
        game_mock = Game.create(id=27001, owner=user_mock, name='Test Game')
        with open(
            (os.path.dirname(__file__))+'/fixtures/game_request.json'
        ) as f:
            json_data = json.load(f)

        mock_request.get(
            "https://www.fake.com/api/Diplomacy/GetGamesAndPlayers?p"
            f"layerIDText=76561190000000007&authKey=test_auth_key",
            json=json_data
        )

        self.assertRaises(
            GameNoLongerExist,
            gmr.get_game_data,
            game_mock
        )