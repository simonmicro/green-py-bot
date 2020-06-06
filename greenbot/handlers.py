import logging
import json
import greenbot.config
import greenbot.repos
import greenbot.util
import greenbot.user
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def start(update, context):
    logging.debug('Command: start')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Hello world!')

def stop(update, context):
    logging.debug('Command: stop')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Bye')
    from greenbot.bot import stop
    stop()

def deactivate(update, context):
    logging.debug('Command: deactivate')

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
    context.bot.send_message(chat_id=update.effective_chat.id, text='User info: ' + str(greenbot.user.User(update.message.chat.id).scripts))

def activate(update, context):
    logging.debug('Command: activate')

    # Show keyboard for repos (if not given)
    if len(context.args) < 1:
        # Show keyboard with key for every repo
        keyboard = []
        for repoName in greenbot.repos.getRepos():
            keyboard.append([InlineKeyboardButton(repoName, callback_data='{"cmd":"activate", "params": ["' + repoName + '"]}')])
        greenbot.util.update_or_reply(update, 'Missing repo param. Please select repo', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Show keyboard for script (if not given)
    if len(context.args) < 2:
        # Show keyboard with key for every script
        keyboard = []
        for scriptName in greenbot.repos.getScripts(context.args[0]):
            keyboard.append([InlineKeyboardButton(scriptName, callback_data='{"cmd":"activate", "params": ["' + context.args[0] + '", "' + scriptName + '"]}')])
        greenbot.util.update_or_reply(update, 'Missing script param. Please select script', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Okay, activate the script
    greenbot.util.update_or_reply(update, 'OK: ' + context.args[0] + ' ' + context.args[1])

def keyboard_button(update, context):
    query = update.callback_query
    logging.debug('Callback: Keyboard button pressed' + str(query.data))
    query.answer()
    # Now try to decode the packed data into commands and args
    try:
        msgData = json.loads(query.data)
        # If successful: Test if the cmd param is set - if yes, forward respectively
        if 'cmd' in msgData.keys():
            logging.debug('Found command data')
            context.args = msgData['params']
            if msgData['cmd'] == 'activate':
                activate(update, context)
            else:
                logging.error('Command not allowed inside callback!')
        else:
            logging.error('Keyboard press didn\'t contain any supported operation')
    except json.decoder.JSONDecodeError as e:
        # Ignore the data and inform user about error
        logging.error('Error at JSON data parsing: ' + str(e))
        pass
