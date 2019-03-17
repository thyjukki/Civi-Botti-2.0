import json
import os
from unittest import TestCase

import requests_mock

from civbot import gmr
from civbot.exceptions import InvalidAuthKey


class TestGmr(TestCase):

    def test_get_steam_id_from_auth(self):
        auth_key = os.getenv('TEST_AUTH_KEY')
        steam_id = os.getenv('TEST_STEAM_ID')
        self.assertEqual(steam_id, gmr.get_steam_id_from_auth(auth_key))

    def test_get_steam_id_from_auth_invalid(self):
        self.assertRaises(
            InvalidAuthKey,
            gmr.get_steam_id_from_auth,
            'null'
        )

    @requests_mock.Mocker()
    def test_get_games_should_return_list_of_games(self, mock_request):
        with open((os.path.dirname(__file__))+'/fixtures/game_request.json') as f:
            json_data = json.load(f)

        game_data = json_data['Games']

        mock_request.get(requests_mock.ANY, json=json_data)

        games = gmr.get_games(os.getenv('TEST_STEAM_ID'), os.getenv('TEST_AUTH_KEY'))

        self.assertEqual(game_data, games)
