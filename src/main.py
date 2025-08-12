from datetime import datetime
from random import randint, shuffle

import pandas as pd
import numpy as np

import telebot
from telebot import types

from users import users

file = "../data/verben.csv"

with open("../token.txt", "r") as f:
    token = f.read()

token = token.replace("\n", "")
bot = telebot.TeleBot(token, parse_mode=None)

user_state = []
users_dict = users

verben = pd.read_csv(file, usecols=["verben"]).values.flatten().tolist()
preps = pd.read_csv(file, usecols=["präpositionen"]).values.flatten().tolist()

chat_id = 0

def get_random():
    idx = randint(0, len(verben)-1)
    return [idx, verben[idx], preps[idx]]

def transform(s):
    s = s.replace(" ", "")
    return s.lower()

@bot.message_handler(commands=["start"])
def send_welcome(message):
    username = str(message.from_user.username)
    user_id = str(message.from_user.id)

    bot.send_message(message.chat.id, f"Herzlich wilkommen @{username}! Bist du bereit, Verben mit den richtigen Präpositionen zu verbinden?", parse_mode="Markdown")
    bot.send_message(message.chat.id, "Schreib /s um zu spielen oder /h um um Hilfe zu bitten", parse_mode="Markdown")

    d = str(datetime.now())
    with open("../users.txt", "a") as f:
        if len(username) == 0:
            username = user_id

        print(f"{username} has connected - {d}")
        f.write(username + ": " + d + "\n")

@bot.message_handler(commands=["h"])
def help(message):
    bot.reply_to(message, "Moglichkeiten: \n/s - spielen \n/p - Punktzahl zeigen \n/r - Punktzahl resetten \n/h - Hilfe")

@bot.message_handler(commands=["resetten", "r"])
def reset(message):
    username = str(message.from_user.username)
    user_id = str(message.from_user.id)

    if len(username) == 0:
        username = user_id

    users_dict[username] = 0
    bot.reply_to(message, f"Deine Punktzahl ist jetzt {users_dict[username]}")

@bot.message_handler(commands=["p"])
def show_score(message):
    bot.reply_to(message, f"{users_dict}")

@bot.message_handler(commands=["s"])
def play(message):
    global chat_id, verben, preps
    
    username = str(message.from_user.username)
    user_id = str(message.from_user.id)

    if len(username) == 0:
        username = user_id

    users_dict.setdefault(username, 0)

    markup = types.ReplyKeyboardMarkup(row_width=3)
    bot.send_message(message.chat.id, f"{chat_id} - Mit welcher Präposition kann dieses Verb verbunden werden?")

    correct = get_random()
    s1 = get_random()
    s2 = get_random()

    prepositions = [correct[2], s1[2], s2[2]]
    while prepositions[0] == prepositions[1] or prepositions[0] == prepositions[2] or prepositions[1] == prepositions[2]:
        s1 = get_random()
        s2 = get_random()
        prepositions = [correct[2], s1[2], s2[2]]

    user_state.append(correct[2])

    verben.pop(correct[0])
    preps.pop(correct[0])

    if len(verben) <= 3:
        verben = pd.read_csv(file, usecols=["verben"]).values.flatten().tolist()
        preps = pd.read_csv(file, usecols=["präpositionen"]).values.flatten().tolist()

    shuffle(prepositions)

    o1 = types.KeyboardButton("/" + prepositions[0])
    o2 = types.KeyboardButton("/" + prepositions[1])
    o3 = types.KeyboardButton("/" + prepositions[2])
    markup.add(o1, o2, o3)  

    bot.reply_to(message, f"{correct[1]}", reply_markup=markup)

    @bot.message_handler(func=lambda message: True)
    def verify(message):
        markup = types.ReplyKeyboardRemove(selective=False)

        user_answer = transform(message.text[1:])
        correct_answer = user_state[chat_id-1]

        if user_answer == transform(correct_answer):
            bot.reply_to(message, f"Richtig! Die Antwort ist '{correct_answer}'", reply_markup=markup)
            users_dict[username] += 1
        else:
            bot.reply_to(message, f"Falsch! Die Antwort war '{correct_answer}'", reply_markup=markup)
            if users_dict[username] != 0:
                users_dict[username] -= 1

        bot.send_message(message.chat.id, f"Die Punktzahl von @{username} ist: {users_dict[username]}")

        with open("users.py", "w") as f:
            f.write("users = " + str(users_dict) + "\n")

    chat_id += 1


print("Bot is up!")

bot.infinity_polling()
