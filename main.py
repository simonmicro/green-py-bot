#!/usr/bin/python3

import logging
import greenbot.bot

# Prepare logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

# Start the bot itself...
greenbot.bot.start()
