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
    context.bot.send_message(chat_id=update.effective_chat.id, text='Hi! I am a bot ' + random.choice(['😏', '🤪']) + ', programmed to execute scripts by your schedule. To begin you should activate a new script with /activate. You can use /info to view all currently active scripts and their last execution result. If you don\'t find what you are looking for, maybe consider to program it yourself 💻! Its easy - It is just Python 🐍!')

def stop(update, context):
    logging.debug('Command: stop')
    context.bot.send_message(chat_id=update.effective_chat.id, text='🆘 Initiating bot shutdown...')
    from greenbot.bot import stop
    stop()

def onError(update, context):
    greenbot.util.updateOrReply(update, random.choice(['🤯', '🤬', '😬', '🥴']) + ' I am broken...')
    raise context.error

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
        scriptsStr = 'Currently active scripts are:\n\n'
        for identifier in greenbot.user.get(update.message.chat.id).getScripts():
            scriptsStr = scriptsStr + user.getScriptSchedule(identifier).getLastRunEmoji() + ' ' + identifier + ' \(' + str(user.getScriptSchedule(identifier)) + '\)\n'
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
    greenbot.util.updateOrReply(update, random.choice(['👻', '🥳', '😁']) + ' Yay, it has been activated! Now use 👉 /schedule ' + scriptIdentifier + ' 👈 to execute it whenever you need...')

def schedule(update, context):
    logging.debug('Command: schedule')

    scriptIdentifier = greenbot.util.getUserSkriptIdentifier(update, context, 'schedule', 'Which from your scripts do you mean ' + random.choice(['🤔', '🤨']) + '?')
    if not scriptIdentifier:
        return

    user = greenbot.user.get(update.effective_chat.id)
    scriptSchedule = user.getScriptSchedule(scriptIdentifier)

    # Show the current schedule if no params are given
    if len(context.args) == 2:
        if context.args[1] == 'useInterval':
            scriptSchedule.enableInterval()
            user.write()
        elif context.args[1] == 'useDayTime':
            scriptSchedule.enableDayTime()
            user.write()

    if len(context.args) < 2 or context.args[1] == 'useInterval' or context.args[1] == 'useDayTime':
        keyboard = []
        if scriptSchedule.usesInterval():
            keyboard.append([InlineKeyboardButton('~ Not implemented yet ~', callback_data='42')])
            keyboard.append([InlineKeyboardButton('Switch to day/time', callback_data='schedule ' + context.args[0] + ' useDayTime')])
        else:
            keyboard.append([InlineKeyboardButton('Edit days', callback_data='schedule ' + context.args[0] + ' editDays'),
                InlineKeyboardButton('Edit times', callback_data='schedule ' + context.args[0] + ' editTime')])
            keyboard.append([InlineKeyboardButton('Switch to interval', callback_data='schedule ' + context.args[0] + ' useInterval')])
        greenbot.util.updateOrReply(update, '🕒 The current schedule is ' + str(scriptSchedule), reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Toggle the day as requested
    if context.args[1] == 'toggleDay':
        scriptSchedule.toggleDay(int(context.args[2]))
        user.write()

    # Show menu for setting day(s) if called with editDays
    if context.args[1] == 'editDays' or context.args[1] == 'toggleDay':
        keyboard = []
        for dayId in range(0, 7):
            sign = ''
            if dayId in scriptSchedule.getDays():
                sign = '✅'
            else:
                sign = '❌'
            keyboard.append([InlineKeyboardButton(sign + ' ' + greenbot.schedule.Schedule.dayToString(dayId) + ' ' + sign, callback_data='schedule ' + context.args[0] + ' toggleDay ' + str(dayId))])
        keyboard.append([InlineKeyboardButton('Back', callback_data='schedule ' + context.args[0])])
        greenbot.util.updateOrReply(update, 'Select your active days...', reply_markup=InlineKeyboardMarkup(keyboard))

    # Apply the requested time change
    if context.args[1] == 'addTime':
        scriptSchedule.addTime(context.args[2])
        user.write()

    # Show menu for setting time/interval if called with editTime
    if context.args[1] == 'editTime' or context.args[1] == 'addTime' or context.args[1] == 'setInterval':
        keyboard = []
        keyboard.append([InlineKeyboardButton('Add 00:00', callback_data='schedule ' + context.args[0] + ' addTime 00:00'),
            InlineKeyboardButton('Add 08:00', callback_data='schedule ' + context.args[0] + ' addTime 08:00'),
            InlineKeyboardButton('Add 12:00', callback_data='schedule ' + context.args[0] + ' addTime 12:00')])
        keyboard.append([InlineKeyboardButton('Back', callback_data='schedule ' + context.args[0])])
        greenbot.util.updateOrReply(update, '🕒 The current schedule is ' + str(scriptSchedule), reply_markup=InlineKeyboardMarkup(keyboard))
        return

def deactivate(update, context):
    logging.debug('Command: deactivate')

    scriptIdentifier = greenbot.util.getUserSkriptIdentifier(update, context, 'deactivate', 'Yes, yes - I see. Which script should I ' + random.choice(['fire 😎', 'disable 😬', 'remove 😬']) + '?')
    if not scriptIdentifier:
        return

    # Okay, activate the script
    greenbot.user.get(update.effective_chat.id).deactivateScript(context.args[0])
    greenbot.util.updateOrReply(update, random.choice(['💀', '💣', '😵']) + ' Bye ' + context.args[0] + '. You have been deactivated.')

def keyboard_button(update, context):
    query = update.callback_query
    logging.debug('Callback: Keyboard button pressed ' + str(query.data))
    query.answer()

    # Now try to decode the packed data into commands and args
    msgData = query.data.split(' ')
    cmd = msgData[0]
    context.args = msgData[1:]
    logging.debug('Found command ' + cmd + ' with params ' + str(context.args))
    if cmd == 'activate':
        activate(update, context)
    elif cmd == 'schedule':
        schedule(update, context)
    elif cmd == 'deactivate':
        deactivate(update, context)
    elif cmd == 'script_info':
        script_info(update, context)
    else:
        logging.error('Command "' + cmd + '" not allowed inside callback!')
