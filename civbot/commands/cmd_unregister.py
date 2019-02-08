import telegram
from telegram import ReplyKeyboardRemove
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters

from civbot.commands.cmd_cancel import cancel_all
from civbot.models import User

VERIFY = 1


def unregister(bot, update):
    user = User.get_or_none(User.id == update.message.from_user.id)

    if not user:
        update.message.reply_text("You are not registered!")
        return ConversationHandler.END

    custom_keyboard = [['Yes'], ['No']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)

    update.message.reply_text(
        "Are you sure you want to unregister."
        "You will stop receiving notifications from current games."
        "Your steam id is still kept in order for active games to function."
        "You can register back anytime to continue receiving notifications.",
        reply_markup=reply_markup
    )
    return VERIFY


def verify(bot, update):
    user = User.get(User.id == update.message.from_user.id)

    msg = update.message.text

    reply_markup = telegram.ReplyKeyboardRemove()
    if msg == 'Yes':
        user.delete_instance()
        update.message.reply_text(
            "Unregistered, your user data was removed!",
            reply_markup=reply_markup
        )
        return ConversationHandler.END

    update.message.reply_text(
        "Canceling unregistering, your data was not removed!",
        reply_markup=reply_markup
    )
    return ConversationHandler.END


def handle():

    return ConversationHandler(
        entry_points=[CommandHandler('unregister', unregister, filters=Filters.private)],

        states={
            VERIFY: [MessageHandler(Filters.text, verify)],
        },

        fallbacks=[CommandHandler('cancel', cancel_all)]
    )
