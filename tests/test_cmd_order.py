from unittest import TestCase
from unittest.mock import Mock, patch

from peewee import SqliteDatabase

from civbot.commands import cmd_order
from civbot.models import database_proxy, User, Subscription, Game


class TestOrder(TestCase):
    def test_order_should_fail_if_no_games_in_chat(self):
        database = SqliteDatabase(':memory:')
        database_proxy.initialize(database)
        database.create_tables([User, Game, Subscription])

        bot_mock = Mock()
        update_mock = Mock()
        update_mock.message.from_user.id = 0

        cmd_order.order(bot_mock, update_mock)
        update_mock.message.reply_text.assert_called_with(
            'No games added to this chat'
        )

    def test_order_should_fail_if_game_does_not_exist_anymore(self):
        self.fail()

    def test_order_should_display_order_of_players(self):
        self.fail()
