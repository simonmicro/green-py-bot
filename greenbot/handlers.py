import logging
import greenbot.config
import greenbot.repos
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def start(update, context):
    logging.debug('Command: start')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Hello world!')

def stop(update, context):
    logging.debug('Command: stop')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Bye')
    from greenbot.bot import stop
    stop()

def activate(update, context):
    logging.debug('Command: activate')
    if len(context.args) != 2:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Missing params: [repo] [script]')

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

def test_keyboard(update, context):
    logging.debug('Command: test_keyboard')
    keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
                 InlineKeyboardButton("Option 2", callback_data='2')],

                [InlineKeyboardButton("Option 3", callback_data='3')],

                [InlineKeyboardButton("Option 1", callback_data='1'),
                InlineKeyboardButton("Option 2", callback_data='2'),
                InlineKeyboardButton("Option 3", callback_data='3'),
                InlineKeyboardButton("Option 4", callback_data='4'),
                InlineKeyboardButton("Option 5", callback_data='5')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)

def test_keyboard_button(update, context):
    logging.debug('Callback: test_keyboard_button')
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text="Selected option: {}".format(query.data))
