import os

import requests

from civbot.exceptions import InvalidAuthKey, GameNoLongerExist


def get_steam_id_from_auth(authkey) -> str:
    url = os.getenv('GMR_URL') + "/api/Diplomacy/AuthenticateUser?authKey=" + authkey
    print(authkey)

    r = requests.get(url)
    if r.text == 'null':
        raise InvalidAuthKey()
    return r.text


def get_games(steam_id, authorization_key) -> list:
    url = os.getenv('GMR_URL') + \
          f"/api/Diplomacy/GetGamesAndPlayers?playerIDText={steam_id}&authKey={authorization_key}"

    r = requests.get(url)

    return r.json()['Games']


def get_game_data(game):
    url = os.getenv('GMR_URL') + \
          f"/api/Diplomacy/GetGamesAndPlayers?playerIDText={game.owner.steam_id}&authKey={game.owner.authorization_key}"

    r = requests.get(url)

    for data in r.json()['Games']:
        if data['GameId'] == game.id:
            return data

    raise GameNoLongerExist
