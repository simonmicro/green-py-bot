def update_or_reply(update, *args, **kwargs):
    # Detect if we are inside a callback (in that case we will update the msg) or just inside a handler
    if update.message is not None:
        # Okay, no callback -> reply with new msg
        return update.message.reply_text(*args, **kwargs)
    else:
        # Triggred by callback -> edit last msg
        return update.callback_query.edit_message_text(*args, **kwargs)
