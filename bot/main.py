import difflib

import telebot
from telebot import types
from dadata import Dadata
import data
import database
import check_update
import threading

from users_bot import *

bot = telebot.TeleBot(data.TOKEN_API)
db = database.DataBase()
time_checker = check_update.TimeChecker(db)
time_checker.start()


print("База данных загружена")

token_dadata = data.TOKEN_DADATA
secret = data.SECRET_DADATA


def mailing():
    while True:
        if time_checker.content_is_updated():
            info_content = db.update_content()

            for chat, info in chats_info.items():
                if info['register'] and 'add' in info_content and info['group'] in info_content['add']:
                    for content in info_content['add'][info['group']]:
                        bot.send_message(chat, content)


mailing_thread = threading.Thread(target=mailing)
mailing_thread.start()


def register(message):

    all_names = db.read_info_students()
    possible_name = Dadata(token_dadata, secret).clean("name", message.text)['result']

    max = 0
    class_group = ''
    max_name = ''
    group_category = []

    if possible_name:
        for student in all_names:
            if difflib.SequenceMatcher(None, possible_name, student[0]).ratio() > max:
                try:
                    max = difflib.SequenceMatcher(None, possible_name, student[0]).ratio()
                    max_name = student[0]
                    class_group = str(student[1]) + student[2]
                    group_category = student[3]
                except TypeError:
                    continue

            if max == 1:
                break

    if max < 0.5 or not possible_name:
        bot.send_message(message.chat.id, "Извините, я вас не понимаю")
    else:
        markup_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_yes = types.KeyboardButton("Да")
        btn_no = types.KeyboardButton("Нет")

        markup_main.add(btn_yes, btn_no)
        bot.send_message(message.chat.id, "Вы " + max_name + " из " + class_group + "?", reply_markup=markup_main)
        chats_info[message.chat.id]['name'] = max_name
        chats_info[message.chat.id]['group'] = group_category
        print(group_category)
        chats_status[message.chat.id] = 'CONFIRM'


def begin(message):
    pass


def confirm(message):
    if message.text == "Да":
        chats_status[message.chat.id] = "BEGIN"
        chats_info[message.chat.id]['start'] = True
        chats_info[message.chat.id]['register'] = True
        remove = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, f"Здравствуйте, {message.from_user.first_name}!\n"
                                          f"Вы успешно авторизованы как {chats_info[message.chat.id]['name']}.",
                         reply_markup=remove)

        for cur_group in chats_info[message.chat.id]['group']:
            print(cur_group)
            for links in db.read_info_content(group=cur_group).values():
                print(links)
                for link in links:
                    print(link)
                    bot.send_message(message.chat.id, link)

    elif message.text == 'Нет':
        start_message(message)


funcs = {
    "REGISTER": register,
    "BEGIN": begin,
    "CONFIRM": confirm,
}


@bot.message_handler(commands=['start', 'restart'])
def start_message(message):
    bot.send_message(message.chat.id, "Введите ФИО для регистрации")
    chats_info[message.chat.id] = {
        "start": False,
        "name": None,
        "register": False,
        "group": None
    }
    chats_status[message.chat.id] = "REGISTER"


@bot.message_handler(content_types=['text'])
def text_func(message):
    try:
        chat_status = chats_status[message.chat.id]
        funcs[chat_status](message)
    except KeyError:
        bot.send_message(message.chat.id, "Чат не зарегистрирован! Пройдите регистрацию")
        start_message(message)


bot.polling(none_stop=True)
