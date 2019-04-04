import io

from gtts import tts
from telegram.ext import CommandHandler

from civbot.models import Subscription


def tee(bot, update):
    chat_id = update.message.chat_id

    subscription = Subscription.get_or_none(chat_id == chat_id)

    if not subscription:
        update.message.reply_text('No games added to this chat')
        return

    if not subscription.game.ongoing():
        update.message.reply_text('Game is over')
        return

    message = 'Teetkö sen vuoros {}'.format(
        subscription.game.current_player().get_name(bot)
    )

    voice = tts.gTTS(text=message, lang='fi')
    mp3_fp = io.BytesIO()
    voice.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    bot.send_voice(chat_id=chat_id, voice=mp3_fp)

    update.message.reply_text(message)


def handle():
    return CommandHandler('tee', tee)
