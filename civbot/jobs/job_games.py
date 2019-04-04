from steamwebapi import profiles

from civbot import gmr
from civbot.models import Game, User, Player
from civbot.exceptions import GameNoLongerExist


def poll_game(bot, game):

    try:
        data = gmr.get_game_data(game)
    except GameNoLongerExist:
        game.active = False
        game.save()
        return False

    if game.subscriptions.count() == 0:
        return False

    if game.current_steam_id == data['CurrentTurn']['UserId']:
        return False

    game.current_steam_id = data['CurrentTurn']['UserId']
    game.save()

    player = Player.get(Player.steam_id == game.current_steam_id)
    if player.registered_user():
        player_name = f'@{player.get_name(bot)}'
    else:
        player_name = player.get_name(bot)
    #
    for subscription in game.subscriptions:
        bot.send_message(
            chat_id=subscription.chat_id,
            text=f"It's now your turn {player_name}"
        )

    return True


def poll_games(bot, job):
    for game in Game.select():
        if game.active:
            poll_game(bot, game)
