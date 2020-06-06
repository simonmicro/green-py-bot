import logging
import json
import greenbot.config
import greenbot.handlers
import greenbot.bot
import greenbot.repos

# Prepare logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Load config
greenbot.config.load()

# Register bot and prepare handlers
greenbot.bot.init()

# Start the bot itself...
greenbot.bot.start()

# Update the local repos
greenbot.repos.update()
