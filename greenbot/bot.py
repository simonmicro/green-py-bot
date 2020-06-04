import logging
import greenbot.config
from telegram.ext import Updater
from telegram.ext import CommandHandler

updater = None

def init():
    global updater
    global dispatcher

    # Init telegram
    updater = Updater(token=greenbot.config.token, use_context=True)

    # Install handlers
    updater.dispatcher.add_handler(CommandHandler('start', greenbot.handlers.start))
    updater.dispatcher.add_handler(CommandHandler('stop', greenbot.handlers.stop))

def start():
    logging.info('Starting...')
    global updater

    updater.start_polling()

def stop():
    logging.info('Stopping...')
    global updater

    updater.stop()
