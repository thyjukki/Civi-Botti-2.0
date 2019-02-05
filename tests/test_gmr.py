import os
from unittest import TestCase
from civbot import gmr
from civbot.exceptions import InvalidAuthKey


class TestGmr(TestCase):

    def test_get_steam_id_from_auth(self):
        auth_key = os.getenv('TEST_AUTH_KEY')
        steam_id = os.getenv('TEST_STEAM_ID')
        self.assertEquals(steam_id, gmr.get_steam_id_from_auth(auth_key))

    def test_get_steam_id_from_auth_invalid(self):
        self.failureException(
            InvalidAuthKey,
            gmr.get_steam_id_from_auth('NULL')
        )
