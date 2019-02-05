import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram.ext import Updater
from dotenv import load_dotenv

import models

from commands import cmd_start, cmd_register

engine = None


def main():
    global session
    load_dotenv()
    db_engine = create_engine('sqlite:///db.sqlite', echo=True)
    models.base_model.BaseModel.metadata.create_all(db_engine)
    session_builder = sessionmaker(bind=db_engine)
    session = session_builder()

    try:
        updater = Updater(token=os.environ['TG_TOKEN'])
    except KeyError:
        print("Please set the environment variable TG_TOKEN")
        sys.exit(1)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(cmd_start.handle(session))

    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
