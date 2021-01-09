import telegram
import yfinance as yf
from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, ConversationHandler,  MessageHandler, Filters, CallbackContext, CallbackQueryHandler, PicklePersistence
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

logger = logging.getLogger(__name__)

TOKEN = None

with open("token.txt") as f:
    TOKEN = f.read().strip()

make_persistence = PicklePersistence(filename='data')

def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu

# Dictionary of all the stock symbols
stocks = dict()


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome! I am keep-stock bot, a bot to help you keep track of current stock market prices. "+
    "Use /add SYMBOL to add a new stock for me to keep track or use /show to see details for any particular stock. Use /delete SYMBOL to remove a stock from my memory "+
    "and use /update to retrieve the most recent information")

def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

def add(update, context):
    try:
        reply = context.args[0]
    
        entry = yf.Ticker(reply)
        entry.info
        # Add the new entry into the stocks dictionary
        stocks[reply] = entry
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply+" is successfully added")
    except Exception:
        update.message.reply_text("Please add a new entry by using '/add SYMBOL' or your ticker symbol is not found")

def delete(update, context):
    name = context.args[0]
    try:
        stocks.pop(name)
        update.message.reply_text(name + " is deleted from the list")
    except Exception:
        update.message.reply_text("Error, I cannot find an entry with the symbol "+name)
    
def show(update, context):
    # Display the list of stocks
    list_of_stocks = list()

    for key in stocks:
        list_of_stocks.append(key)
        
    if len(list_of_stocks) == 0:
        update.message.reply_text("The list is empty. Use /add to add new entries")
        return

    button_list = []
    for each in list_of_stocks:
       button_list.append(InlineKeyboardButton(each, callback_data = each))
    reply_markup=InlineKeyboardMarkup(build_menu(button_list,n_cols=2)) #n_cols = 1 is for single column and mutliple rows
    context.bot.send_message(chat_id=update.message.chat_id, text='Choose from the following',reply_markup=reply_markup)


    
def price_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    symbol = query.data

    if symbol.startswith("more"):
        new_symbol = symbol.replace('more', '')
        context.bot.send_message(query.message.chat_id, text="Selected Option: "+new_symbol)
        stock = stocks[new_symbol]
        reply = stock.info
        for i in reply:
            context.bot.send_message(query.message.chat_id, text=i+": "+str(reply[i]))
        
    else:
        context.bot.send_message(query.message.chat_id, text=f"Selected Option: {query.data}")
        stock = stocks[symbol]
        reply = stock.info
        #context.bot.send_message(query.message.chat_id, text="previousClose: "+ reply["previousClose"] + "\nregularMarketOpen: "+reply["regularMarketOpen"])
        button_list = [
        InlineKeyboardButton("more", callback_data='more'+str(symbol))
        ]
        reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
        context.bot.send_message(chat_id=update.effective_chat.id, text="previousClose: "+ str(reply["previousClose"]) + "\nregularMarketOpen: "+str(reply["regularMarketOpen"]), reply_markup=reply_markup)


def update_info(update, context):
    for key in stocks:
        stocks[key] = yf.Ticker(key)

    update.message.reply_text("Success!")


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token=TOKEN, persistence=make_persistence, use_context=True)
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # simple start function
    dispatcher.add_handler(CommandHandler("start", start))

    # Add a new entry
    dispatcher.add_handler(CommandHandler("add", add))

    # Delete an entry
    dispatcher.add_handler(CommandHandler("delete", delete))

    # Show the details and all the entries
    dispatcher.add_handler(CommandHandler("show", show))

    # Update to the lastest data 
    dispatcher.add_handler(CommandHandler("update", update_info))

    # Add unknown
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    # Add price callback
    dispatcher.add_handler(CallbackQueryHandler(price_callback))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()