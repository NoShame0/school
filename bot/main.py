import difflib
import time

import telebot
from telebot import types

from dadata import Dadata

from bot import create, data, load
import parse
import read

import database

from users_bot import *

bot = telebot.TeleBot(data.TOKEN_API)
sh = parse.GoogleSheet()

time.sleep(60)
db = database.DataBase()
print("База данных загружена")

token_dadata = data.TOKEN_DADATA
secret = data.SECRET_DADATA


def register(message):

    session = create.create_session()
    all_names = [(student['name'], student['parallel'], student['group']) for student in read.elements_students(session)]

    possible_name = Dadata(token_dadata, secret).clean("name", message.text)['result']

    max = 0
    class_group = ''
    max_name = ''

    if possible_name:
        for student in all_names:
            if difflib.SequenceMatcher(None, possible_name, student[0]).ratio() > max:
                try:
                    max = difflib.SequenceMatcher(None, possible_name, student[0]).ratio()
                    max_name = student[0]
                    class_group = str(student[1]) + student[2]
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
        chats_status[message.chat.id] = 'CONFIRM'

    session.close()


def begin(message):
    pass


def confirm(message):
    if message.text == "Да":
        chats_status[message.chat.id] = "BEGIN"
        remove = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, f"Здравствуйте, {message.from_user.first_name}!\n"
                                          f"Вы успешно авторизованы как {chats_info[message.chat.id]['name']}.",
                         reply_markup=remove)


funcs = {
    "REGISTER": register,
    "BEGIN": begin,
    "CONFIRM": confirm,
}


@bot.message_handler(commands=['start', 'restart'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет, введи имя!")
    chats_info[message.chat.id] = {
        "start": False,
        "name": None,
        "register": False,
    }
    chats_status[message.chat.id] = "REGISTER"


@bot.message_handler(content_types=['text'])
def text_func(message):
    chat_status = chats_status[message.chat.id]
    funcs[chat_status](message)


bot.polling(none_stop=True)


