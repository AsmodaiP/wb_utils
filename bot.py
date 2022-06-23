from email import message
from multiprocessing.spawn import import_main_path
from typing import List
from dotenv import load_dotenv
import os

import telegram
from telegram import Bot, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)
import change_price
import update_google
import change_name
from cmp_pars import CardInfo, get_info_by_query


CHANGE_PRICE = 'Поменять цену'
CHANGE_NAME = 'Поменять имя'
GET_CPM = 'Получить ставки'

MAIN_MENU = (
    [KeyboardButton(CHANGE_PRICE)],
    [KeyboardButton(CHANGE_NAME)],
    [KeyboardButton(GET_CPM)],
)

CANCEL = (
    [KeyboardButton('/cancel')],
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
WHITELIST = os.environ['WHITELIST'].split(',')
ID_FOR_LOGS = os.environ['ID_FOR_LOGS'].split(',')


def start(bot: Bot, update):
    bot.message.reply_text('Главное меню', reply_markup=MAIN_MENU_MARKUP)


updater = Updater(token=TOKEN)
bot1: Bot = telegram.Bot(TOKEN)


def log_message_wrapper(func, *args, **kwargs):
    def wrapper(bot, update):
        chat_id = bot.message.chat_id
        first_name = bot.message.chat.first_name
        last_name = bot.message.chat.last_name
        username = bot.message.chat.username
        text = bot.message.text
        result = func(bot, update)
        bot1.send_message(chat_id=1126541068,
                          text=f'Пользователь {first_name} {last_name} (@{username}), сообщение: {text}')
        return result
    return wrapper


start_handler = CommandHandler('start', start)
updater.dispatcher.add_handler(start_handler)


@log_message_wrapper
def get_article(bot, update):
    if str(bot['message']['chat']['id']) not in WHITELIST:
        bot.message.reply_text(
            'Операция запрещена, для получения доступа обратитесь к @dmitriy_pereguda')
        return ConversationHandler.END
    bot.message.reply_text(
        'Введите артикул (номер карточки)',
        reply_markup=CANCEL_MARKUP)
    return 'get_current_info'


@log_message_wrapper
def get_current_info(bot, update):
    try:
        article = int(bot.message.text.strip())
    except BaseException:
        bot.message.reply_text(
            'Артикул должен быть числом (внутренний артикул вб). Начните заново')
        return ConversationHandler.END
    info = change_price.get_info_current_price(article)
    if info is None:
        bot.message.reply_text('Артикул не найден')
        return ConversationHandler.END
    update.user_data['article'] = article
    bot.message.reply_text(
        f'Текущая цена {info["price"]},\n Cкидка {info["discount"]} \n Промокод {info["promoCode"]} \n Окончательная цена {info["Цена после скидок"]}')
    bot.message.reply_text(
        'Введите новую цену или отмените операцию',
        reply_markup=CANCEL_MARKUP)
    return 'change_price'


@log_message_wrapper
def change_price_by_bot(bot, update):
    chat_id = bot.message.chat_id
    first_name = bot.message.chat.first_name
    last_name = bot.message.chat.last_name
    username = bot.message.chat.username
    if bot.message.text.strip() == 'Отмена':
        start(bot, update)
        return ConversationHandler.END
    new_price = int(bot.message.text.strip())
    article = update.user_data['article']
    result = change_price.change_price(article, new_price, chat_id)
    update.user_data['article'] = None
    update.user_data['new_price'] = None
    bot.message.reply_text(result)
    bot1.send_message(chat_id=-732179382,
                     text=f'Пользователь {first_name} {last_name} (@{username}), результат:\n {result}')
    update_google.update_table(
        article=article,
        new_price=new_price,
        user_id=f"{first_name} {last_name} {username} {chat_id}")
    start(bot, update)
    return ConversationHandler.END


def cancel(bot, update):
    bot.message.reply_text('Операция отменена', reply_markup=MAIN_MENU_MARKUP)
    return ConversationHandler.END


@log_message_wrapper
def get_new_name(bot, update):
    try:
        article = int(bot.message.text.strip())
    except BaseException:
        bot.message.reply_text(
            'Артикул должен быть числом (внутренний артикул вб). Начните заново')
        return ConversationHandler.END
    update.user_data['article'] = article
    bot.message.reply_text('Введите новое имя')
    return 'change_name'


@log_message_wrapper
def change_name_by_bot(bot, update):
    imtId = update.user_data['article']
    new_name = bot.message.text.strip()
    if change_name.update_name_by_imtID(imtId, new_name):
        bot.message.reply_text('Успешно')
    else:
        bot.message.reply_text('У ВБ что-то пошло не так :( ')
    start(bot, update)
    return ConversationHandler.END


change_price_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.text(
        [CHANGE_PRICE]), get_article)],
    states={
        'get_current_info': [MessageHandler(Filters.text & ~Filters.command, get_current_info)],
        'change_price': [MessageHandler(Filters.text & ~Filters.command, change_price_by_bot)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)


change_name_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.text(
        [CHANGE_NAME]), get_article)],
    states={
        'get_current_info': [MessageHandler(Filters.text & ~Filters.command, get_new_name)],
        'change_name': [MessageHandler(Filters.text & ~Filters.command, change_name_by_bot)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)


@log_message_wrapper
def get_query(bot, update):
    bot.message.reply_text('Введите запрос', reply_markup=CANCEL_MARKUP)
    return 'get_cpm'


@log_message_wrapper
def get_cpm(bot, update):
    query = bot.message.text.strip()
    msg = ''
    i = 0
    result = None
    while i < 3:
        result = None
        msg = ''
        try:
            results: List[CardInfo] = get_info_by_query(query)
            for result in results:
                msg += f'Позиция {result.position}, ставка {result.cpm} \n'
        except BaseException:
            pass
        if len(msg) != 0:
            break
    if len(msg) == 0:
        msg = 'Ставки найти не удалось'
    bot.message.reply_text(msg)
    start(bot, update)
    return ConversationHandler.END


get_cpm_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.text(
        [GET_CPM]), get_query)],
    states={
        'get_cpm': [MessageHandler(Filters.text & ~Filters.command, get_cpm)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)


updater.dispatcher.add_handler(change_name_handler)
updater.dispatcher.add_handler(change_price_handler)
updater.dispatcher.add_handler(get_cpm_handler)
updater.start_polling()
# bot.send_message(chat_id=-732179382,
#                  text=f'Тест')
