import greenbot.config
from telegram.ext import Updater
from telegram.ext import CommandHandler

updater = None

def init():
    global updater
    global dispatcher

    # Load config
    greenbot.config.load()

    # Init telegram
    updater = Updater(token=greenbot.config.token, use_context=True)

    # Install handlers
    start_handler = CommandHandler('start', greenbot.handlers.start)
    updater.dispatcher.add_handler(start_handler)

def run():
    global updater

    updater.start_polling()
