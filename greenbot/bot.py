import logging
import greenbot.config
import greenbot.handlers
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext import MessageHandler
from telegram.ext.filters import Filters

updater = None

def init():
    global updater
    global dispatcher

    # Init telegram
    updater = Updater(token=greenbot.config.token, use_context=True)

    # Install handlers
    updater.dispatcher.add_handler(CommandHandler(['start', 'help'], greenbot.handlers.start))
    updater.dispatcher.add_handler(CommandHandler('store', greenbot.handlers.store))
    updater.dispatcher.add_handler(CommandHandler('info', greenbot.handlers.info))
    updater.dispatcher.add_handler(CommandHandler('activate', greenbot.handlers.activate))
    updater.dispatcher.add_handler(CommandHandler('schedule', greenbot.handlers.schedule))
    updater.dispatcher.add_handler(CommandHandler('deactivate', greenbot.handlers.deactivate))
#    updater.dispatcher.add_handler(CommandHandler('stop', greenbot.handlers.stop))

    updater.dispatcher.add_handler(CallbackQueryHandler(greenbot.handlers.onButton))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, greenbot.handlers.onMessage))

    # And error handlers...
    updater.dispatcher.add_error_handler(greenbot.handlers.onError)

def start():
    logging.info('Starting...')
    global updater

    updater.start_polling()

def stop():
    logging.info('Stopping...')
    global updater

    updater.stop()
