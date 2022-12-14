import difflib

import telebot
from dadata import Dadata

from bot import create, data
import parse
import read

bot = telebot.TeleBot(data.TOKEN_API)
sh = parse.GoogleSheet()

chats_status = {}
token_dadata = data.TOKEN_DADATA
secret = data.SECRET_DADATA


def register(message):

    session = create.create_session()
    all_names = [(student['name'], student['parallel'], student['group']) for student in read.elements(session)]

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
        bot.send_message(message.chat.id, "Вы " + max_name + " из " + class_group + "?")

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
