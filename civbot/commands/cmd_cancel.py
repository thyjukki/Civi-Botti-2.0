import telegram
from telegram.ext import ConversationHandler


def cancel_all(bot, update):
    update.message.reply_text(
        'Canceled',
        reply_markup=telegram.ReplyKeyboardRemove()
    )
    return ConversationHandler.END
