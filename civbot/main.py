import os
import sys
import logging

from peewee import SqliteDatabase
from telegram.ext import Updater

from civbot.commands import cmd_register, cmd_unregister, cmd_start, \
    cmd_new_game, cmd_add_game
from civbot.jobs import job_games
from civbot.models import database_proxy, User, Game, Subscription


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    database = SqliteDatabase('db.sqlite')

    database_proxy.initialize(database)
    database.create_tables([User, Game, Subscription])
    try:
        updater = Updater(token=os.environ['TG_TOKEN'])
    except KeyError:
        print("Please set the environment variable TG_TOKEN")
        sys.exit(1)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(cmd_start.handle())
    dispatcher.add_handler(cmd_register.handle())
    dispatcher.add_handler(cmd_unregister.handle())
    dispatcher.add_handler(cmd_new_game.handle())
    dispatcher.add_handler(cmd_add_game.handle())

    updater.job_queue.run_repeating(job_games.poll_games, interval=30, first=0)
    updater.job_queue.start()
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
