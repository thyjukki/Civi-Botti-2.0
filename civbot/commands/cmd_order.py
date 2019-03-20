from telegram.ext import CommandHandler, ConversationHandler
from civbot.models import User


def order(bot, update):
    update.message.reply_text(
        "test"
    )


def handle():
    return CommandHandler('register', order)
