import time
import logging
import schedule
import greenbot.config
import greenbot.handlers
import greenbot.repos
import greenbot.util
import greenbot.user
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext import MessageHandler
from telegram.ext.filters import Filters

updater = None
logger = logging.getLogger('greenbot')

## Startup the bot by loading config, users and handlers. Schedules the repo updates every 24h. Then enter the main loop.
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
    updater.dispatcher.add_handler(CommandHandler(['start', 'help'], greenbot.util.showTypingAction(greenbot.handlers.start)))
    updater.dispatcher.add_handler(CommandHandler('store', greenbot.util.showTypingAction(greenbot.handlers.store)))
    updater.dispatcher.add_handler(CommandHandler('info', greenbot.util.showTypingAction(greenbot.handlers.info)))
    updater.dispatcher.add_handler(CommandHandler('activate', greenbot.util.showTypingAction(greenbot.handlers.activate)))
    updater.dispatcher.add_handler(CommandHandler('schedule', greenbot.util.showTypingAction(greenbot.handlers.schedule)))
    updater.dispatcher.add_handler(CommandHandler('deactivate', greenbot.util.showTypingAction(greenbot.handlers.deactivate)))
    updater.dispatcher.add_handler(CommandHandler('run', greenbot.util.showTypingAction(greenbot.handlers.run)))
#    updater.dispatcher.add_handler(CommandHandler('stop', greenbot.util.showTypingAction(greenbot.handlers.stop)))

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

## Inform the main loop to stop after the next run
def stop():
    global updater
    logger.info('Stopping...')
    updater.stop()
