from telegram import ReplyKeyboardRemove
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters

import gmr
from civbot.models import User

AUTHKEY = 1


def register(bot, update):
    user = User.get_or_none(User.id == update.message.from_user.id)

    if user:
        bot.send_message(chat_id=update.message.chat_id, text="You are already registered!")
        return ConversationHandler.END

    bot.send_message(
        chat_id=update.message.chat_id,
        text="Provide GMR Authentication key"
        "Authentication key can be acquired from http://multiplayerrobot.com/Download"
    )

    return AUTHKEY


def authkey(bot, update):
    auth_key = gmr.get_steam_id_from_auth(update.message.text)

    if auth_key == 'null':
        bot.send_message(chat_id=update.message.chat_id, text="Authkey incorrect, try again (/cancel to end)")
        return AUTHKEY

    pass


def cancel(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="You are already registered!",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def handle():

    return ConversationHandler(
        entry_points=[CommandHandler('register', register)],

        states={
            AUTHKEY: [MessageHandler(Filters.text, authkey, pass_user_data=True)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
