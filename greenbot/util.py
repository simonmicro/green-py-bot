import random
import logging
import greenbot.repos
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
logger = logging.getLogger('greenbot.util')

## Edits the last sent message or sends a new one (based on event type)
# @param update
# @param *args
# @param **kwargs
# @return sent message
def updateOrReply(update, *args, **kwargs):
    # Detect if we are inside a callback (in that case we will update the msg) or just inside a handler
    if update.callback_query is not None:
        # Triggered by callback -> edit last msg
        return update.callback_query.edit_message_text(*args, **kwargs)
    else:
        # Okay, no callback -> reply with new msg
        return update.effective_message.reply_text(*args, **kwargs)

## Asks the user to input the details, needed to build a script identifier as first param for the given command
# @param update
# @param context
# @param commandName We will execute 'commandName scriptIdentifier'
# @param missingRepoOut
# @param missingScriptOut
# @return scripts identifier (at least partly)
def getGlobalSkriptIdentifier(update, context, commandName, missingRepoOut = 'Okay, now tell me in which repository I should look 🤔', missingScriptOut = 'And which script do you mean ' + random.choice(['🧐', '🤨']) + '?'):
    # Are we missing the identifier or is it invalid?
    if len(context.args) < 1 or not greenbot.repos.resolveIdentifier(context.args[0])[0] in greenbot.repos.getRepos():
        keyboard = []
        for repoName in greenbot.repos.getRepos():
            keyboard.append([InlineKeyboardButton(repoName, callback_data=commandName + ' ' + greenbot.repos.makeIdentifier(repoName))])
        greenbot.util.updateOrReply(update, missingRepoOut, reply_markup=InlineKeyboardMarkup(keyboard))
        return False
    # ...or the script part? (Intended, if we are showing the keyboard)
    elif not greenbot.repos.resolveIdentifier(context.args[0])[1] in greenbot.repos.getScripts(greenbot.repos.resolveIdentifier(context.args[0])[0]):
        # Show keyboard with key for every script
        keyboard = []
        for scriptName in greenbot.repos.getScripts(greenbot.repos.resolveIdentifier(context.args[0])[0]):
            keyboard.append([InlineKeyboardButton(scriptName, callback_data=commandName + ' ' + greenbot.repos.makeIdentifier(context.args[0], scriptName))])
        keyboard.append([InlineKeyboardButton('Back', callback_data=commandName)])
        greenbot.util.updateOrReply(update, missingScriptOut, reply_markup=InlineKeyboardMarkup(keyboard))
        return False

    return context.args[0]

## Ask the user which of his identifiers he want
# @param update
# @param context
# @param commandName
# @param missingIdentifierOut
# @return scripts identifier (at least partly)
def getUserSkriptIdentifier(update, context, commandName, missingIdentifierOut):
    # Make sure the user has at least one script to select
    if len(greenbot.user.get(update.effective_chat.id).getScripts()) < 1:
        greenbot.util.updateOrReply(update, 'You have currently no scripts activated ' + random.choice(['😢', '😱', '🥶']) + '. Use /activate to begin your journey!')
        return False

    # Show keyboard for active scripts
    if len(context.args) < 1 or not greenbot.repos.validateIdentifier(context.args[0]):
        # Show keyboard with key for every active script
        keyboard = []
        for scriptIdentifier in greenbot.user.get(update.effective_chat.id).getScripts():
            keyboard.append([InlineKeyboardButton(scriptIdentifier, callback_data=commandName + ' ' + scriptIdentifier)])
        greenbot.util.updateOrReply(update, missingIdentifierOut, reply_markup=InlineKeyboardMarkup(keyboard))
        return False

    return context.args[0]

## Executes virtual commands from e.g. the context or a button press
# @param update
# @param context
# @param cmdStr Normal command from e.g. the chat (just without the leading '/')
def executeVirtualCommand(update, context, cmdStr):
    import greenbot.handlers

    # Now try to decode the packed data into commands and args
    msgData = cmdStr.split(' ')
    cmd = msgData[0]
    context.args = msgData[1:]
    logger.debug('Found command ' + cmd + ' with params ' + str(context.args))
    if cmd == 'activate':
        greenbot.handlers.activate(update, context)
    elif cmd == 'schedule':
        greenbot.handlers.schedule(update, context)
    elif cmd == 'deactivate':
        greenbot.handlers.deactivate(update, context)
    elif cmd == 'store':
        greenbot.handlers.store(update, context)
    elif cmd == 'run':
        greenbot.handlers.run(update, context)
    else:
        logger.error('Command "' + cmd + '" not allowed inside callback!')

## If chat type is not PRIVATE, make sure the user is admin (this also shows an error is the check is False)
# @param update
# @return Is the user priviledged?
def isGroupAdminOrDirectChat(update):
    if update.effective_message is not None and update.effective_user is not None and update.effective_chat.type != update.effective_chat.PRIVATE:
        # Okay as first get list of admins for the chat
        admins = update.effective_chat.get_administrators()
        # Now make sure the sender is in that admin list...
        for chatMember in admins:
            if chatMember.user == update.effective_user:
                return True
        greenbot.util.updateOrReply(update, random.choice(['👮‍♂️', '👮‍♀️', '😡', '😬']) + random.choice([' Sorry, you are not allowed to do that!', ' Nope. Ask an admin for assistance.', ' Access denied until further notice.']))
        logger.info('User id ' + str(update.effective_user) + ' tried to access a restricted command. Access denied.')
        return False
    return True
