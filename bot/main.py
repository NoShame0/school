import difflib
import sys

import keyboard
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


mailing_stop = False


def mailing():

    while not mailing_stop:
        if time_checker.content_is_updated():
            info_content = db.update_content()

            # for chat, info in chats_info.items():
            chats = db.read_chats_info()
            print(chats)
            for chat, info in chats.items():
                if info['register'] and 'add' in info_content:
                    for group in info['group']:
                        if group in info_content['add']:
                            for type_content, content in info_content['add'][group].items():
                                if content:
                                    for link in content:
                                        bot.send_message(chat, link)

    return 0


mailing_thread = threading.Thread(target=mailing, daemon=True)
mailing_thread.start()


def register(message):

    all_names = db.read_info_students()
    possible_name = message.text

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
        chat_info = {
            message.chat.id: {
                "start": True,
                "name": max_name,
                "register": True,
                "group": group_category,
                "status": "BEGIN",
                "class_group": class_group,
            },
        }

        bot.register_next_step_handler_by_chat_id(message.chat.id, confirm, chat_info)



def begin(message):
    bot.send_message(message.chat.id, "Извините, я вас не понимаю")


def confirm(message, update_params):
    if message.text == "Да":

        bot.send_message(message.chat.id, f"Здравствуйте, {message.from_user.first_name}!\n"
                                          f"Вы успешно авторизованы как {update_params[message.chat.id]['name']}.\n"
                                          f"Хотите получить подборку полезных для вас ссылок?",
                         )

        db.chats_update(update_params)
        bot.register_next_step_handler_by_chat_id(message.chat.id, mail_all_content)

    else:
        start_message(message)


funcs = {
    "REGISTER": register,
    "BEGIN": begin,
    "CONFIRM": confirm,
}


def mail_all_content(message):
    remove = types.ReplyKeyboardRemove()

    if message.text == 'Да':

        bot.send_message(message.chat.id, "Подборка полезных ссылок:", reply_markup=remove)

        groups_of_chat = db.read_chats_info(chat_id=message.chat.id)
        for cur_group in groups_of_chat[message.chat.id]['group']:
            for links in db.read_info_content(group=cur_group).values():

                for links_type in links.values():
                    if links_type:
                        for link in links_type:
                            bot.send_message(message.chat.id, link)

        bot.send_message(message.chat.id, "Скоро появяться новые ссылки, не пропустите!")
    else:
        bot.send_message(message.chat.id, "Сюда будут присылаться полезные ссылки, не пропустите!", reply_markup=remove)

    bot.register_next_step_handler_by_chat_id(message.chat.id, begin)


@bot.message_handler(commands=['start', 'restart'])
def start_message(message):
    remove = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Введите ФИО для регистрации", reply_markup=remove)

    chat_info = {
        message.chat.id: {
            "start": False,
            "name": None,
            "register": False,
            "group": None,
            'status': "REGISTER",
            "class_group": None,
        }
    }

    db.chats_update(chat_info)
    bot.register_next_step_handler_by_chat_id(message.chat.id, register)


@bot.message_handler(commands=['stop'])
def stop_bot(message):
    bot.send_message(message.chat.id, message.chat.id)
    bot.stop_bot()


@bot.message_handler(content_types=['text'])
def text_func(message):
    try:
        # chat_status = chats_status[message.chat.id]
        chat_status = db.read_chats_info(chat_id=message.chat.id)[message.chat.id]['status']
        funcs[chat_status](message)
    except KeyError:
        bot.send_message(message.chat.id, "Чат не зарегистрирован! Пройдите регистрацию")
        start_message(message)


bot.polling(non_stop=True)
