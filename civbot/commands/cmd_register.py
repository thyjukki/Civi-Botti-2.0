from telegram import ReplyKeyboardRemove
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters

import gmr
from civbot.models import User
from civbot.exceptions import InvalidAuthKey

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
    try:
        steam_id = gmr.get_steam_id_from_auth(update.message.text)
    except InvalidAuthKey:
        bot.send_message(chat_id=update.message.chat_id, text="Authkey incorrect, try again (/cancel to end)")
        return AUTHKEY

    User.create(
        id=update.message.from_user.id,
        steam_id=steam_id,
        authorization_key=update.message.text
    )

    bot.send_message(
        chat_id=update.message.chat_id,
        text=f"Successfully registered with steam id {steam_id}"
    )

    return ConversationHandler.END


def cancel(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Canceled!",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def handle():

    return ConversationHandler(
        entry_points=[CommandHandler('register', register, filters=Filters.private)],

        states={
            AUTHKEY: [MessageHandler(Filters.text, authkey)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
