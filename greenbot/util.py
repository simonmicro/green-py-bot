def updateOrReply(update, *args, **kwargs):
    print(update.effective_message)
    # Detect if we are inside a callback (in that case we will update the msg) or just inside a handler
    if update.callback_query is not None:
        # Triggered by callback -> edit last msg
        return update.callback_query.edit_message_text(*args, **kwargs)
    else:
        # Okay, no callback -> reply with new msg
        return update.effective_message.reply_text(*args, **kwargs)

def getChatID(update):
    print(update.effective_chat)
    # Detect if we are inside a callback or just inside a handler
    if update.effective_chat is not None:
        # No callback
        return update.effective_chat.id
    else:
        # Triggered by callback? Just try an other approach
        return update.callback_query.message.chat.id
