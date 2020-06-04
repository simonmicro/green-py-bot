import logging

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
