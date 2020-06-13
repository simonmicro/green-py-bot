import time
import sys
import logging
import schedule
import greenbot.config
import greenbot.bot
import greenbot.repos
import greenbot.user

# Prepare logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logging.info('Starting...')

# Load config
greenbot.config.load()

# And preload the user cache (otherwise we would not activate the schedules correctly...)
greenbot.user.getAll()

# Register bot and prepare handlers
greenbot.bot.init()

# Start the bot itself...
greenbot.bot.start()

# Update the local repos
greenbot.repos.update()

# Schedue some maintenance job(s)
schedule.every().day.do(greenbot.repos.update)

logging.info('Started The Green Bot #' + greenbot.config.version + '.')

while greenbot.bot.updater.running:
    logging.debug('Executing pending jobs...')
    schedule.run_pending()
    time.sleep(10)

logging.info('Stopped.')
sys.exit()
