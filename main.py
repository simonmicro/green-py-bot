import logging
import json
import greenbot.config
import greenbot.handlers
import greenbot.bot

# Prepare logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

# Register bot and prepare handlers
greenbot.bot.init()

# Start the bot itself...
greenbot.bot.run()
