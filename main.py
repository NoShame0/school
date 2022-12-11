import difflib

import telebot
from dadata import Dadata

import create
import data
import parse
import read

bot = telebot.TeleBot(data.TOKEN_API)
sh = parse.GoogleSheet()

chats_status = {}
token_dadata = data.TOKEN_DADATA


def register(message):

    session = create.create_session()
    all_names = [(student['name'], student['parallel'], student['group']) for student in read.elements(session)]
    possible_names = [possible_fio['value'] for possible_fio in Dadata(token_dadata).suggest("fio", message.text)]

    max = 0
    max_name = ''
    for possible_name in possible_names:
        for student in all_names:
            if difflib.SequenceMatcher(None, possible_name, student[0]).ratio() > max:
                max = difflib.SequenceMatcher(None, possible_name, student[0]).ratio()
                max_name = student[0]

            if max == 1:
                break
        if max == 1:
            break

    bot.send_message(message.chat.id, max_name + "    " + str(max))
    session.close()


funcs = {
    "REGISTER": register,
}


@bot.message_handler(commands=['start', 'restart'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет, введи имя!")
    chats_status[message.chat.id] = "REGISTER"


@bot.message_handler(content_types=['text'])
def text_func(message):
    funcs["REGISTER"](message)


bot.polling(none_stop=True)
