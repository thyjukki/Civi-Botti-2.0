from telegram.ext import CommandHandler, ConversationHandler

from civbot.models import Subscription, Player


def order(bot, update):
    chat_id = update.message.chat_id

    subscription = Subscription.get_or_none(chat_id == chat_id)

    if not subscription:
        update.message.reply_text('No games added to this chat')
        return

    if not subscription.game.ongoing():
        update.message.reply_text('Game is over')
        return

    message = 'Order is:'
    for player in subscription.game.players.order_by(Player.order):
        message += f"\n{player.get_name(bot)}"

    update.message.reply_text(message)


def handle():
    return CommandHandler('order', order)
