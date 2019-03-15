import telegram
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters

from civbot import gmr
from civbot.commands.cmd_cancel import cancel_all
from civbot.models import User, Game, Subscription

SELECT = 1


def add_game(bot, update):
    user = User.get_or_none(User.id == update.message.from_user.id)

    if not user:
        update.message.reply_text('You are not registered!')
        return ConversationHandler.END

    chat_id = update.message.chat_id
    admin_ids = [admin.user.id for admin in bot.get_chat_administrators(chat_id)]
    if update.message.from_user.id not in admin_ids:
        update.message.reply_text('You are not admin of the group!')
        return ConversationHandler.END

    games = user.games

    if len(games) == 0:
        update.message.reply_text("You don't have any registered games")
        return ConversationHandler.END

    games = list(
        filter(
            lambda g: not (
                Subscription.select().where(Subscription.game == g).where(Subscription.chat_id == chat_id).exists()
            ),
            games
        )
    )

    if len(games) == 0:
        update.message.reply_text("You don't have any registered games not in this chat")
        return ConversationHandler.END

    custom_keyboard = []
    for game in games:
        custom_keyboard.append([game.name])
    custom_keyboard.append(['cancel'])
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)

    update.message.reply_text('Chose the game', reply_markup=reply_markup)

    return SELECT


def select_game(bot, update):
    if update.message.text == 'cancel':
        update.message.reply_text('Canceled', reply_markup=telegram.ReplyKeyboardRemove)
        return ConversationHandler.END

    user = User.get_or_none(User.id == update.message.from_user.id)

    game = [g for g in user.games if g.name == update.message.text]

    if len(game) == 0:
        update.message.reply_text('Game does not exist', reply_markup=telegram.ReplyKeyboardRemove)
        return ConversationHandler.END
    game = game[0]

    chat_id = update.message.chat_id
    if Subscription.select().where(Subscription.game == game).where(Subscription.chat_id == chat_id).exists():
        update.message.reply_text('Game has already been added', reply_markup=telegram.ReplyKeyboardRemove)
        return ConversationHandler.END

    Subscription.create(
        game=game,
        chat_id=chat_id
    )

    update.message.reply_text(
        f'Subscribed to {game.name}. This chat will now start receiving notifications for the '
        'game. To get notifications, send /register to me as private message',
        reply_markup=telegram.ReplyKeyboardRemove)

    return ConversationHandler.END


def handle():

    return ConversationHandler(
        entry_points=[CommandHandler('addgame', add_game)],

        states={
            SELECT: [MessageHandler(Filters.text, select_game)],
        },

        fallbacks=[CommandHandler('cancel', cancel_all)]
    )
