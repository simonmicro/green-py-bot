import time
import logging
import schedule
import greenbot.config
import greenbot.handlers
import greenbot.repos
import greenbot.user
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext import MessageHandler
from telegram.ext.filters import Filters

updater = None
logger = logging.getLogger('greenbot')

def start():
    global updater

    logger.info('Starting...')

    # Load config
    greenbot.config.load()

    # And preload the user cache (otherwise we would not activate the schedules correctly...)
    greenbot.user.getAll()

    # Init telegram
    updater = Updater(token=greenbot.config.token, use_context=True)

    # Install handlers
    updater.dispatcher.add_handler(CommandHandler(['start', 'help'], greenbot.handlers.start))
    updater.dispatcher.add_handler(CommandHandler('store', greenbot.handlers.store))
    updater.dispatcher.add_handler(CommandHandler('info', greenbot.handlers.info))
    updater.dispatcher.add_handler(CommandHandler('activate', greenbot.handlers.activate))
    updater.dispatcher.add_handler(CommandHandler('schedule', greenbot.handlers.schedule))
    updater.dispatcher.add_handler(CommandHandler('deactivate', greenbot.handlers.deactivate))
    updater.dispatcher.add_handler(CommandHandler('run', greenbot.handlers.run))
#    updater.dispatcher.add_handler(CommandHandler('stop', greenbot.handlers.stop))

    updater.dispatcher.add_handler(CallbackQueryHandler(greenbot.handlers.onButton))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, greenbot.handlers.onMessage))

    # And error handlers...
    updater.dispatcher.add_error_handler(greenbot.handlers.onError)

    # Update the local repos
    greenbot.repos.update()

    # Schedue some maintenance job(s)
    schedule.every().day.do(greenbot.repos.update)

    # And begin with the main loop
    updater.start_polling()

    logger.info('Started The Green Bot #' + greenbot.config.version + '.')
    while greenbot.bot.updater.running:
        logger.debug('Executing pending jobs...')
        schedule.run_pending()
        time.sleep(10)

    logger.info('Stopped.')

def stop():
    global updater
    logger.info('Stopping...')
    updater.stop()
