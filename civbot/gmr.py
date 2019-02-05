import requests

from civbot.exceptions import InvalidAuthKey


host = "http://multiplayerrobot.com"


def get_steam_id_from_auth(authkey: str) -> str:
    url = host + "/api/Diplomacy/AuthenticateUser?authKey=" + authkey

    r = requests.get(url)
    if r.text == 'null':
        raise InvalidAuthKey()
    return r.text
