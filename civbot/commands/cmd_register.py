from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters

from civbot import gmr
from civbot.commands.cmd_cancel import cancel_all
from civbot.exceptions import InvalidAuthKey
from civbot.models import User

AUTHKEY = 1


def register(bot, update):
    user = User.get_or_none(User.id == update.message.from_user.id)

    if user:
        update.message.reply_text("You are already registered!")
        return ConversationHandler.END

    update.message.reply_text(
        "Provide GMR Authentication key"
        "Authentication key can be acquired from http://multiplayerrobot.com/Download"
    )

    return AUTHKEY


def authkey(bot, update):
    try:
        steam_id = gmr.get_steam_id_from_auth(update.message.text)
    except InvalidAuthKey:
        update.message.reply_text("Authkey incorrect, try again (/cancel to end)")
        return AUTHKEY

    User.create(
        id=update.message.from_user.id,
        steam_id=steam_id,
        authorization_key=update.message.text
    )

    update.message.reply_text(f"Successfully registered with steam id {steam_id}")

    return ConversationHandler.END


def handle():

    return ConversationHandler(
        entry_points=[CommandHandler('register', register, filters=Filters.private)],

        states={
            AUTHKEY: [MessageHandler(Filters.text, authkey)],
        },

        fallbacks=[CommandHandler('cancel', cancel_all)]
    )
