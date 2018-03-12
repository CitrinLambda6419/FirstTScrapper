import telebot
import threading
from threading import Timer
from threading import Thread
from time import sleep
import time
from datetime import datetime
import functools

token = "#"
bot = telebot.TeleBot("#")
bot.get_me()

list_of_users = []
list_of_message = []
can_wright = True


def add_message(message):
    for convert in message:
        not_sent_yet = True
        while not_sent_yet:
            if can_wright:
                list_of_message.append(convert)
                not_sent_yet = False
            else:
                time.sleep(1)


def check_user_existence(object):
    return (object in list_of_users)


def add_user(user):
    if check_user_existence(user):
        return False
    else:
        list_of_users.append(user)
        return True


def delete_user(user):
    if check_user_existence(user):
        list_of_users.remove(user)
        return True
    else:
        return False


def bot_send_message(user_id, message):
    bot.send_message(user, message)


def send_message_for_all_users(message):
    if message != "":
        for user_id in list_of_users:
            bot.send_message(user_id, message)


def message_thread():
    while True:
        if list_of_message != []:
            can_wright = False
            send_message_for_all_users(list_of_message.pop(0))
            can_wright = True
        time.sleep(2)


def polling_thread():
    bot.polling(none_stop=False, interval=2, timeout=0)


@bot.message_handler(commands=["start"])
def handle_text(message):
    if (add_user(message.chat.id)):
        bot.send_message(message.chat.id, "Вы добавлены в рассылку.")
    else:
        bot.send_message(message.chat.id, "Вы уже находитесь в рассылке.")


@bot.message_handler(commands=["stop"])
def handle_text(message):
    if (delete_user(message.chat.id)):
        bot.send_message(message.chat.id, "Вы удалены из рассылки.")
    else:
        bot.send_message(message.chat.id, "Вас не было в рассылке.")


@bot.message_handler(commands=["help"])
def handle_text(message):
    bot.send_message(message.chat.id, " /Start Подписаться на рассылку. \n /Stop Отписаться от рассылки.")


t1 = threading.Thread(target=message_thread, args=[])
t2 = threading.Thread(target=polling_thread, args=[])


def start_bot():
    t1.start()
    t2.start()
