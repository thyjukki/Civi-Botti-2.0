from civbot import gmr
from civbot.models import Game
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
    player_name = game.current_steam_id
    for subscription in game.subscriptions:
        bot.send_message(
            chat_id=subscription.chat_id,
            text=f"It's now your turn {player_name}"
        )

    return True


def poll_games(bot, job):
    for game in Game.select():
        poll_game(bot, game)
