import telegram
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, \
    Filters

from civbot import gmr
from civbot.commands.cmd_cancel import cancel_all
from civbot.models import User, Game, Player

SELECT = 1


def new_game(bot, update):
    user = User.get_or_none(User.id == update.message.from_user.id)

    if not user:
        update.message.reply_text('You are not registered!')
        return ConversationHandler.END

    games = gmr.get_games(user.steam_id, user.authorization_key)

    if len(games) == 0:
        update.message.reply_text('You are not part of any games')
        return ConversationHandler.END

    games = list(
        filter(
            lambda x: not Game.select().where(Game.id == x['GameId']).exists(),
            games
        )
    )

    if len(games) == 0:
        update.message.reply_text('No games to be added')
        return ConversationHandler.END

    custom_keyboard = []
    for game in games:
        custom_keyboard.append([game['Name']])
    custom_keyboard.append(['cancel'])
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)

    update.message.reply_text('Chose the game', reply_markup=reply_markup)

    return SELECT


def select_game(bot, update):
    if update.message.text == 'cancel':
        update.message.reply_text(
            'Canceled',
            reply_markup=telegram.ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    user = User.get_or_none(User.id == update.message.from_user.id)

    games = gmr.get_games(user.steam_id, user.authorization_key)
    games_data = [g for g in games if g['Name'] == update.message.text]

    if len(games_data) == 0:
        update.message.reply_text(
            'Game does not exist',
            reply_markup=telegram.ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    game_data = games_data[0]

    if Game.select().where(Game.id == game_data['GameId']).exists():
        update.message.reply_text(
            'Game already registered',
            reply_markup=telegram.ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    game = Game.create(
        id=game_data['GameId'],
        owner=user,
        name=game_data['Name'],
        current_steam_id=game_data['CurrentTurn']['UserId']
    )

    for player in game_data['Players']:
        Player.create(
            steam_id=player['UserId'],
            game=game,
            order=player['TurnOrder']
        )

    update.message.reply_text(
        f'Game {game.name} registered',
        reply_markup=telegram.ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def handle():

    return ConversationHandler(
        entry_points=[
            CommandHandler('newgame', new_game, filters=Filters.private)
        ],

        states={
            SELECT: [MessageHandler(Filters.text, select_game)],
        },

        fallbacks=[CommandHandler('cancel', cancel_all)]
    )
