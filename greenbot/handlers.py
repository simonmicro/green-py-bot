import logging
import json
import schedule
import greenbot.config
import greenbot.repos
import greenbot.util
import greenbot.user
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def start(update, context):
    logging.debug('Command: start')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Hello world!')

def stop(update, context):
    logging.debug('Command: stop')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Bye')
    from greenbot.bot import stop
    stop()

def next_run(update, context):
    logging.debug('Command: next_run')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Next run scheduled at ' + str(schedule.next_run()))

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
    if len(context.args) != 2:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Missing params: [repo] [script]')
    context.bot.send_message(chat_id=update.effective_chat.id, text=greenbot.repos.getModule(context.args[0], context.args[1]).info())

def user_info(update, context):
    logging.debug('Command: user_info')
    scriptsStr = '```\n'
    for identifier in greenbot.user.get(update.message.chat.id).getScripts():
        scriptsStr = scriptsStr + identifier + '\n'
    scriptsStr = scriptsStr + '\n```'
    context.bot.send_message(chat_id=update.effective_chat.id, text='Currently active scripts ' + scriptsStr, parse_mode=telegram.ParseMode.MARKDOWN_V2)

def activate(update, context):
    logging.debug('Command: activate')

    # Show keyboard for repos (if not given)
    if len(context.args) < 1:
        # Show keyboard with key for every repo
        keyboard = []
        for repoName in greenbot.repos.getRepos():
            keyboard.append([InlineKeyboardButton(repoName, callback_data='{"cmd":"activate", "params": ["' + repoName + '"]}')])
        greenbot.util.updateOrReply(update, 'Missing repo param. Please select repo', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Show keyboard for script (if not given)
    if len(context.args) < 2 or not greenbot.repos.validateIdentifier(greenbot.repos.makeIdentifier(context.args[0], context.args[1])):
        # Show keyboard with key for every script
        keyboard = []
        for scriptName in greenbot.repos.getScripts(context.args[0]):
            keyboard.append([InlineKeyboardButton(scriptName, callback_data='{"cmd":"activate", "params": ["' + context.args[0] + '", "' + scriptName + '"]}')])
        greenbot.util.updateOrReply(update, 'Missing script param. Please select script', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    skriptIdentifier = greenbot.repos.makeIdentifier(context.args[0], context.args[1])

    # Okay, activate the script
    greenbot.user.get(update.effective_chat.id).activateScript(skriptIdentifier)
    greenbot.util.updateOrReply(update, 'ACTIVATED: ' + skriptIdentifier + '\nNow use /schedule ' + skriptIdentifier + ' to run it whenever you need...')

def schedule(update, context):
    logging.debug('Command: schedule')

    # Are we missing the identifier or is it invalid?
    if len(context.args) < 1 or not greenbot.repos.resolveIdentifier(context.args[0])[0] in greenbot.repos.getRepos():
        keyboard = []
        for repoName in greenbot.repos.getRepos():
            keyboard.append([InlineKeyboardButton(repoName, callback_data='{"cmd":"schedule", "params": ["' + greenbot.repos.makeIdentifier(repoName) + '"]}')])
        greenbot.util.updateOrReply(update, 'Missing repo param. Please select repo', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    # ...or the script part? (Intended, if we are showing the keyboard)
    elif not greenbot.repos.resolveIdentifier(context.args[0])[1] in greenbot.repos.getScripts(greenbot.repos.resolveIdentifier(context.args[0])[0]):
        # Show keyboard with key for every script
        keyboard = []
        for scriptName in greenbot.repos.getScripts(greenbot.repos.resolveIdentifier(context.args[0])[0]):
            keyboard.append([InlineKeyboardButton(scriptName, callback_data='{"cmd":"schedule", "params": ["' + greenbot.repos.makeIdentifier(context.args[0], scriptName) + '"]}')])
        greenbot.util.updateOrReply(update, 'Missing script param. Please select script', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    scriptIdentifier = context.args[0]

    # Okay, 
    greenbot.util.updateOrReply(update, 'RESCHEDULED: ' + scriptIdentifier)

def deactivate(update, context):
    logging.debug('Command: deactivate')
    if len(greenbot.user.get(update.effective_chat.id).getScripts()) < 1:
        greenbot.util.updateOrReply(update, 'No scripts active')
        return

    # Show keyboard for active scripts
    if len(context.args) < 1 or not greenbot.repos.validateIdentifier(context.args[0]):
        # Show keyboard with key for every active script
        keyboard = []
        for scriptIdentifier in greenbot.user.get(update.effective_chat.id).getScripts():
            keyboard.append([InlineKeyboardButton(scriptIdentifier, callback_data='{"cmd":"deactivate", "params": ["' + scriptIdentifier + '"]}')])
        greenbot.util.updateOrReply(update, 'Missing repo and script param. Please select', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Okay, activate the script
    greenbot.user.get(update.effective_chat.id).deactivateScript(context.args[0])
    greenbot.util.updateOrReply(update, 'DEACTIVATED: ' + context.args[0])

def keyboard_button(update, context):
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
            else:
                logging.error('Command "' + msgData['cmd'] + '" not allowed inside callback!')
        else:
            logging.error('Keyboard press didn\'t contain any supported operation')
    except json.decoder.JSONDecodeError as e:
        # Ignore the data and inform user about error
        logging.error('Error at JSON data parsing: ' + str(e))
        pass
