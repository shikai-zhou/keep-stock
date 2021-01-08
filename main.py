import telegram
import yfinance as yf
from telegram.ext import Updater, CommandHandler, ConversationHandler,  MessageHandler, Filters

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


logger = logging.getLogger(__name__)


# Dictionary of all the stock symbols
stocks = dict()

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

def add(update, context):
    reply = context.args
    #try:
    entry = yf.Ticker(reply)
    update.message.reply_text(entry)
    #stocks[reply] = entry
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply+" is successfully added")
    #except Exception :
    #    update.message.reply_text("Please add a new entry by using '/add SYMBOL'")

    
    
def show(update, context):
    for key in stocks:
        context.bot.send_message(chat_id=update.effective_chat.id, text=key)

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    # bot = telegram.Bot(token='1512157486:AAFUjgYJNwFq3kUsm_3K_BYvf670rWKD6eI')
    updater = Updater(token='1512157486:AAFUjgYJNwFq3kUsm_3K_BYvf670rWKD6eI', use_context=True)
    
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # simple start function
    dispatcher.add_handler(CommandHandler("start", start))

    # Add a new entry
    dispatcher.add_handler(CommandHandler("add", add))

    # Show the details and all the entries
    dispatcher.add_handler(CommandHandler("show", show))

    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))

    # Add unknown
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()