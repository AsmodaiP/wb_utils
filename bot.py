from dotenv import load_dotenv
import os

import telegram
from telegram import Bot, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)
import change_price


MAIN_MENU = (
    [KeyboardButton('Поменять цену')],
)

CANCEL = (
    [KeyboardButton('Отмена')],
)


CANCEL_MARKUP = ReplyKeyboardMarkup(
    CANCEL,
    resize_keyboard=True,
    one_time_keyboard=True)

MAIN_MENU_MARKUP = ReplyKeyboardMarkup(
    MAIN_MENU,
    resize_keyboard=True,
    one_time_keyboard=False)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv()

TOKEN = os.environ['TOKEN']
bot: Bot = telegram.Bot(TOKEN)
WHITELIST= os.environ['WHITELIST'].split(',')
def start(bot: Bot, update):
    bot.message.reply_text('Главное меню', reply_markup=MAIN_MENU_MARKUP)

updater = Updater(token=TOKEN)


start_handler = CommandHandler('start', start)
updater.dispatcher.add_handler(start_handler)

def get_article(bot, update):
    if str(bot['message']['chat']['id']) not in WHITELIST:
        bot.message.reply_text('Операция запрещена, для получения доступа обратитесь к @dmitriy_pereguda')
        return ConversationHandler.END
    bot.message.reply_text('Введите артикул')
    return 'get_current_info'

def get_current_info(bot, update):
    try:
        article = int(bot.message.text.strip())
    except:
        bot.message.reply_text('Артикул должен быть числом (внутренний артикул вб). Начните заново')
        return ConversationHandler.END
    info = change_price.get_info_current_price(article)
    if info is None:
        bot.message.reply_text('Артикул не найден')
        return ConversationHandler.END
    update.user_data['article'] = article
    bot.message.reply_text(f'Текущая цена {info["price"]},\n Cкидка {info["discount"]} \n Промокод {info["promoCode"]}')
    bot.message.reply_text('Введите новую цену или отмените операцию', reply_markup=CANCEL_MARKUP)
    return 'change_price'

def change_price_by_bot(bot, update):
    if bot.message.text.strip() == 'Отмена':
        start(bot, update)
        return ConversationHandler.END
    new_price = int(bot.message.text.strip())
    article = update.user_data['article'] 
    result = change_price.change_price(article, new_price)
    bot.message.reply_text(result)
    return ConversationHandler.END

def cancel(bot, update):
    bot.message.reply_text('Операция отменена')
    return ConversationHandler.END

change_price_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.text(
        ['Поменять цену']), get_article)],
    states={
        'get_current_info':[MessageHandler(Filters.text & ~Filters.command, get_current_info)],
        'change_price': [MessageHandler(Filters.text & ~Filters.command, change_price_by_bot)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
    )
updater.dispatcher.add_handler(change_price_handler)
updater.start_polling()



