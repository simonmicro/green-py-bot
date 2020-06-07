import time
import logging
import schedule
import greenbot.config
import greenbot.bot
import greenbot.repos

# Prepare logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

# Load config
greenbot.config.load()

# Register bot and prepare handlers
greenbot.bot.init()

# Start the bot itself...
greenbot.bot.start()

# Update the local repos
greenbot.repos.update()

# Schedue some maintenance job(s)
schedule.every().day.do(greenbot.repos.update)

while greenbot.bot.updater.running:
    logging.debug('Executing pending jobs...')
    schedule.run_pending()
    time.sleep(60)
