import logging
import random
import greenbot.config
import greenbot.repos
import greenbot.util
import greenbot.user
import greenbot.schedule
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup, KeyboardButton

def start(update, context):
    logging.debug('Command: start')
    keyboard = [
        [KeyboardButton('/info')],
        [KeyboardButton('/activate'), KeyboardButton('/store'), KeyboardButton('/deactivate')],
        [KeyboardButton('/schedule')]
    ]
    context.bot.send_message(chat_id=update.effective_chat.id, text='Hi! I am a bot ' + random.choice(['😏', '🤪']) + ', programmed to execute scripts by your schedule. ' +
        'To begin you should activate a new script with /activate. You can use /info to view all currently active scripts and their last execution result. If you don\'t ' + 
        'find what you are looking for, maybe consider to program it yourself 💻! Its easy - It is just Python 🐍!', reply_markup=ReplyKeyboardMarkup(keyboard))

def stop(update, context):
    logging.debug('Command: stop')
    context.bot.send_message(chat_id=update.effective_chat.id, text='🆘 Initiating bot shutdown...')
    from greenbot.bot import stop
    stop()

def store(update, context):
    logging.debug('Command: store')

    scriptIdentifier = greenbot.util.getGlobalSkriptIdentifier(update, context, 'store', 'Welcome to the store 🖖! Before I can show you any of my beautiful scripts, please tell me in which repository you want to take a look...',
        'Good choice - now in which script are you interested?')
    if not scriptIdentifier:
        return

    greenbot.util.updateOrReply(update, 'I like kittens!')

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
    greenbot.util.updateOrReply(update, random.choice(['👻', '🥳', '😁']) + ' Yay, it has been activated! Now use 👉 /schedule ' + scriptIdentifier + ' 👈 to execute it whenever you need (its currently scheduled ' + str(greenbot.user.get(update.effective_chat.id).getScriptSchedule(scriptIdentifier)) + ')...')

def schedule(update, context):
    logging.debug('Command: schedule')

    scriptIdentifier = greenbot.util.getUserSkriptIdentifier(update, context, 'schedule', 'Which from your scripts do you mean ' + random.choice(['🤔', '🤨']) + '?')
    if not scriptIdentifier:
        return

    user = greenbot.user.get(update.effective_chat.id)
    scriptSchedule = user.getScriptSchedule(scriptIdentifier)

    # Show the current schedule if no params are given
    if len(context.args) >= 2:
        if context.args[1] == 'useInterval':
            scriptSchedule.enableInterval()
            user.write()
        elif context.args[1] == 'useDayTime':
            scriptSchedule.enableDayTime()
            user.write()
        elif context.args[1] == 'setInterval':
            # Did the user already appended his new interval?
            if len(context.args) == 3:
                try:
                    scriptSchedule.setInterval(int(context.args[2]))
                    user.write()
                except ValueError:
                    user.setCommandContext('schedule ' + context.args[0] + ' setInterval')
                    context.bot.send_message(chat_id=update.effective_chat.id, text='Thats not a number. Try again.')
                    return
            else:
                # No -> update the command context so the user can send his input into this command
                user.setCommandContext('schedule ' + context.args[0] + ' setInterval')
                context.bot.send_message(chat_id=update.effective_chat.id, text='Okay, send me now the new interval in minutes!')
                return

    if len(context.args) < 2 or context.args[1] == 'useInterval' or context.args[1] == 'useDayTime' or context.args[1] == 'setInterval':
        keyboard = []
        if scriptSchedule.usesInterval():
            keyboard.append([InlineKeyboardButton('Change interval', callback_data='schedule ' + context.args[0] + ' setInterval')])
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
        if len(context.args) == 3:
            try:
                scriptSchedule.addTime(context.args[2])
                user.write()
            except ValueError:
                user.setCommandContext('schedule ' + context.args[0] + ' addTime')
                context.bot.send_message(chat_id=update.effective_chat.id, text='Thats not a valid time. Try again.')
                return
        else:
            # No time given... Ask for one...
            user.setCommandContext('schedule ' + context.args[0] + ' addTime')
            context.bot.send_message(chat_id=update.effective_chat.id, text='Okay, send me the new time formatted like 11:42!')
            return
    if context.args[1] == 'delTime':
        if len(context.args) == 3:
            scriptSchedule.removeTime(context.args[2])
            user.write()
        else:
            # No time given... Show list of available ones...
            if len(scriptSchedule.getTimes()) > 1:
                keyboard = []
                for time in scriptSchedule.getTimes():
                    keyboard.append([InlineKeyboardButton(time, callback_data='schedule ' + context.args[0] + ' delTime ' + time)])
                keyboard.append([InlineKeyboardButton('Back', callback_data='schedule ' + context.args[0] + ' editTime')])
                greenbot.util.updateOrReply(update, 'Which one do you want to remove?', reply_markup=InlineKeyboardMarkup(keyboard))
                return
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text='At least one execution time is needed!')          
                return      

    # Show menu for setting time/interval if called with editTime
    if context.args[1] == 'editTime' or context.args[1] == 'addTime' or context.args[1] == 'delTime' or context.args[1] == 'setInterval':
        keyboard = []
        keyboard.append([InlineKeyboardButton('Add', callback_data='schedule ' + context.args[0] + ' addTime'),
            InlineKeyboardButton('Remove', callback_data='schedule ' + context.args[0] + ' delTime')])
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

def onError(update, context):
    greenbot.util.updateOrReply(update, random.choice(['🤯', '🤬', '😬', '🥴']) + ' I am broken...')
    raise context.error

def onButton(update, context):
    query = update.callback_query
    logging.debug('Callback: Keyboard button pressed ' + str(query.data))
    query.answer()
    greenbot.util.executeVirtualCommand(update, context, query.data)

def onMessage(update, context):
    if greenbot.user.get(update.message.chat.id).getCommandContext() is not None:
        # Always reset the context before executing the virtual command with the context
        cmdContext = greenbot.user.get(update.message.chat.id).getCommandContext()
        greenbot.user.get(update.message.chat.id).setCommandContext(None)
        greenbot.util.executeVirtualCommand(update, context, cmdContext + ' ' + update.message.text)
    # Otherwise we will just ignore the msg of the user...
