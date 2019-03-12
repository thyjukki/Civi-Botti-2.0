import requests

from civbot.exceptions import InvalidAuthKey

host = "http://multiplayerrobot.com"


def get_steam_id_from_auth(authkey: str) -> str:
    url = host + "/api/Diplomacy/AuthenticateUser?authKey=" + authkey

    r = requests.get(url)
    if r.text == 'null':
        raise InvalidAuthKey()
    return r.text


def get_games(steam_id, authorization_key):
    url = host + f"/api/Diplomacy/GetGamesAndPlayers?playerIDText={steam_id}&authKey={authorization_key}"

    r = requests.get(url)

    return r.json()['Games']
