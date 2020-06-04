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
    updater.dispatcher.add_handler(CommandHandler('list_repos', greenbot.handlers.list_repos))
    updater.dispatcher.add_handler(CommandHandler('list_scripts', greenbot.handlers.list_scripts))
    updater.dispatcher.add_handler(CommandHandler('script_info', greenbot.handlers.script_info))
    updater.dispatcher.add_handler(CommandHandler('activate', greenbot.handlers.activate))
    updater.dispatcher.add_handler(CommandHandler('deactivate', greenbot.handlers.deactivate))
    updater.dispatcher.add_handler(CommandHandler('stop', greenbot.handlers.stop))

def start():
    logging.info('Starting...')
    global updater

    updater.start_polling()

def stop():
    logging.info('Stopping...')
    global updater

    updater.stop()
