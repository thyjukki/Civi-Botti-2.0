from telegram.ext import CommandHandler

from civbot.models import User


def start_message(bot, update):
    user = User.get_or_none(User.id == update.message.from_user.id)

    msg = 'Welcome to telegram bot 2.0'

    if not user:
        msg += '\nRun /register to get started'
    bot.send_message(chat_id=update.message.chat_id, text=msg)


def handle():
    return CommandHandler('start', start_message)