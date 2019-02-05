from telegram.ext import CommandHandler

from models.user import User


def start_message(bot, update):
    ed_user = session.query(User).filter(User.id == update.message.from_user.id).first()

    msg = 'Welcome to telegram bot 2.0'

    if not ed_user:
        msg += '\nRun /register to get started'
    bot.send_message(chat_id=update.message.chat_id, text=msg)


def handle(s):
    global session
    session = s

    return CommandHandler('start', start_message)
