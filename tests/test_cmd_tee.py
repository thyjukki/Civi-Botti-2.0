import json
import os
from unittest import TestCase
from unittest.mock import Mock, patch

from peewee import SqliteDatabase

from civbot.commands import cmd_tee
from civbot.models import database_proxy, User, Subscription, Game, Player


class TestTee(TestCase):
    def test_tee_should_fail_if_no_games_in_chat(self):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game, Subscription])

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 0
        update_mock.message.chat_id = 101

        cmd_tee.tee(bot_mock, update_mock)
        update_mock.message.reply_text.assert_called_with(
            'No games added to this chat'
        )

    @patch('civbot.gmr.get_games')
    def test_tee_should_fail_if_game_does_not_exist_anymore(
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

        cmd_tee.tee(bot_mock, update_mock)
        update_mock.message.reply_text.assert_called_with(
            'Game is over'
        )

    @patch('io.BytesIO')
    @patch('gtts.tts.gTTS')
    @patch('steamwebapi.profiles.get_user_profile')
    @patch('civbot.gmr.get_games')
    def test_tee_should_send_voice(
            self,
            get_games_mock,
            mock_get_user_profile,
            mock_gtts,
            mock_voice_fp
    ):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game, Player, Subscription])

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 0
        update_mock.message.chat_id = 1234

        mock_gtts.return_value = mock_gtts
        mock_voice_fp.return_value = mock_voice_fp

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
        mock_get_user_profile.personaname = "Player1"

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

        cmd_tee.tee(bot_mock, update_mock)

        mock_gtts.write_to_fp.assert_called_with(mock_voice_fp)
        mock_voice_fp.seek.assert_called_with(0)
        bot_mock.send_voice.assert_called_with(
            chat_id=update_mock.message.chat_id,
            voice=mock_voice_fp
        )