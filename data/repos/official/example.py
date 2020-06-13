import greenbot.bot

def scheduledRun(user):
    greenbot.bot.updater.bot.send_message(chat_id=user.getUID(), text='Hi from the example script! You will receive this message whenever this script gets executed. Make sure to /deactivate it when you are done.')
