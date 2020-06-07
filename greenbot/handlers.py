import logging
import random
import greenbot.config
import greenbot.repos
import greenbot.util
import greenbot.user
import greenbot.schedule
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def start(update, context):
    logging.debug('Command: start')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Hi! I am a bot 😏, programmed to execute scripts by your schedule. To begin you should activate a new script with /activate. You can use /info to view all currently active scripts and their last execution result. If you don\'t find what you are looking for, maybe consider to program it yourself 💻! Its easy - It is just Python 🐍!')

def stop(update, context):
    logging.debug('Command: stop')
    context.bot.send_message(chat_id=update.effective_chat.id, text='🆘 Initiating bot shutdown...')
    from greenbot.bot import stop
    stop()

def next_run(update, context):
    logging.debug('Command: next_run')
    import schedule
    context.bot.send_message(chat_id=update.effective_chat.id, text='🕒 Next run scheduled at ' + str(schedule.next_run()))

def list_repos(update, context):
    logging.debug('Command: list_repos')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Available repos: ' + ' '.join(greenbot.repos.getRepos()))

def list_scripts(update, context):
    logging.debug('Command: list_scripts')
    if len(context.args) != 1:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Missing params: [repo]')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Available scripts in ' + context.args[0] + ': ' + ' '.join(greenbot.repos.getScripts(context.args[0])))

def script_info(update, context):
    logging.debug('Command: script_info')

    scriptIdentifier = greenbot.util.getGlobalSkriptIdentifier(update, context, 'script_info')
    if not scriptIdentifier:
        return

    context.bot.send_message(chat_id=update.effective_chat.id, text=greenbot.repos.getModule(scriptIdentifier).info())

def info(update, context):
    logging.debug('Command: info')
    user = greenbot.user.get(update.message.chat.id)
    if len(user.getScripts()) > 0:
        scriptsStr = 'Currently active scripts are:\n'
        for identifier in greenbot.user.get(update.message.chat.id).getScripts():
            scriptsStr = scriptsStr + user.getScriptSchedule(identifier).getLastRunEmoji() + ' ' + identifier + '\n'
        context.bot.send_message(chat_id=update.effective_chat.id, text=scriptsStr, parse_mode=telegram.ParseMode.MARKDOWN_V2)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='You have currently no scripts activated ' + random.choice(['😢', '😱', '🥺']) + '. Use /activate to begin your journey!')

def activate(update, context):
    logging.debug('Command: activate')

    scriptIdentifier = greenbot.util.getGlobalSkriptIdentifier(update, context, 'activate')
    if not scriptIdentifier:
        return

    # Okay, activate the script
    greenbot.user.get(update.effective_chat.id).activateScript(scriptIdentifier)
    greenbot.util.updateOrReply(update, random.choice(['👻', '🥳', '😁']) + ' Yay, it has been activated! Now use 👉 /schedule ' + scriptIdentifier + ' 👈 to run it whenever you need...')

def schedule(update, context):
    logging.debug('Command: schedule')

    scriptIdentifier = greenbot.util.getUserSkriptIdentifier(update, context, 'schedule')
    if not scriptIdentifier:
        return

    # Reschedule it for now to run it every minute
    newSchedule = greenbot.schedule.Schedule()
    newSchedule.setInterval(1)
    greenbot.user.get(update.effective_chat.id).setScriptSchedule(scriptIdentifier, newSchedule)
    greenbot.util.updateOrReply(update, 'RESCHEDULED: TO RUN EVERY MINUTE ' + scriptIdentifier)

def deactivate(update, context):
    logging.debug('Command: deactivate')
    if len(greenbot.user.get(update.effective_chat.id).getScripts()) < 1:
        greenbot.util.updateOrReply(update, 'No scripts active')
        return

    scriptIdentifier = greenbot.util.getUserSkriptIdentifier(update, context, 'deactivate')
    if not scriptIdentifier:
        return

    # Okay, activate the script
    greenbot.user.get(update.effective_chat.id).deactivateScript(context.args[0])
    greenbot.util.updateOrReply(update, random.choice(['💀', '💣', '😵']) + ' Bye ' + context.args[0] + '. It has been deactivated.')

def keyboard_button(update, context):
    import json
    query = update.callback_query
    logging.debug('Callback: Keyboard button pressed' + str(query.data))
    query.answer()
    # Now try to decode the packed data into commands and args
    try:
        msgData = json.loads(query.data)
        # If successful: Test if the cmd param is set - if yes, forward respectively
        if 'cmd' in msgData.keys():
            context.args = msgData['params']
            logging.debug('Found command data with params ' + str(context.args))
            if msgData['cmd'] == 'activate':
                activate(update, context)
            elif msgData['cmd'] == 'schedule':
                schedule(update, context)
            elif msgData['cmd'] == 'deactivate':
                deactivate(update, context)
            elif msgData['cmd'] == 'script_info':
                script_info(update, context)
            else:
                logging.error('Command "' + msgData['cmd'] + '" not allowed inside callback!')
        else:
            logging.error('Keyboard press didn\'t contain any supported operation')
    except json.decoder.JSONDecodeError as e:
        # Ignore the data and inform user about error
        logging.error('Error at JSON data parsing: ' + str(e))
        pass
