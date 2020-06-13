import greenbot.bot

# This script will be loaded (imported) on the first call of any method inside of it.

# The implementation of this method is REQUIRED.
def getScriptInfo():
    return {
        'name': 'Example script',
        'author': 'Simonmicro',
        'description': 'A demo script, containing all required and optional method implementations.',
        'version': '1.0.0'
    }

# Gets called on /run - implementation is OPTIONAL.
def manualRun(user, update, context):
    greenbot.bot.updater.bot.send_message(chat_id=user.getUID(), text='Hi. I know you executed me manually 🙃!')

# Gets called on a schedule - implementation is OPTIONAL.
def scheduledRun(user):
    greenbot.bot.updater.bot.send_message(chat_id=user.getUID(), text='💡 Hi from the example script! You will receive this message whenever this script gets executed. Make sure to /deactivate it when you are done.')
