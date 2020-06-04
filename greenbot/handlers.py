import logging
import greenbot.config
import greenbot.repos

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
