from datetime import datetime
import pandas as pd
from random import randint, shuffle

import telebot
from telebot import types

file = "../data/verben.csv"

with open("../token.txt", "r") as f:
    token = f.read()

token = token.replace("\n", "")
bot = telebot.TeleBot(token, parse_mode=None)

user_state = []

verben = pd.read_csv(file, usecols=["verben"]).values.flatten()
preps = pd.read_csv(file, usecols=["präpositionen"]).values.flatten()

def get_random():
    idx = randint(0, len(verben)-1)
    return [idx, verben[idx], preps[idx]]

def transform(s):
    s = s.replace(" ", "")
    return s.lower()

@bot.message_handler(commands=["start"])
def send_welcome(message):
    username = str(message.from_user.username)

    bot.send_message(message.chat.id, f"Herzlich wilkommen @{username}! Bist du bereit, Verben mit den richtigen Präpositionen zu verbinden?", parse_mode="Markdown")
    bot.send_message(message.chat.id, "Schreib /s um zu spielen", parse_mode="Markdown")

    d = str(datetime.now())
    with open("../users.txt", "a") as f:
        print(f"{username} has connected - {d}")
        f.write(username + ": " + d + "\n")

chat_id = 0
score = 0

@bot.message_handler(commands=["resetten", "r"])
def reset(message):
    global score
    score = 0
    bot.reply_to(message, f"Deine Punktzahl ist jetzt {score}")

@bot.message_handler(commands=["s"])
def play(message):
    global chat_id

    markup = types.ReplyKeyboardMarkup(row_width=3)
    bot.send_message(message.chat.id, f"{chat_id} - Mit welcher Präposition kann dieses Verb verbunden werden?")

    correct = get_random()
    s1 = get_random()
    s2 = get_random()

    prepositions = [correct[2], s1[2], s2[2]]
    while len(prepositions) < 3:
        s1 = get_random()
        s2 = get_random()
        prepositions = [correct[2], s1[2], s2[2]]

    user_state.append(correct[2])

    shuffle(prepositions)

    o1 = types.KeyboardButton("/" + prepositions[0])
    o2 = types.KeyboardButton("/" + prepositions[1])
    o3 = types.KeyboardButton("/" + prepositions[2])
    markup.add(o1, o2, o3)  

    bot.reply_to(message, f"{correct[1]}", reply_markup=markup)

    @bot.message_handler(func=lambda message: True)
    def verify(message):
        global score

        markup = types.ReplyKeyboardRemove(selective=False)

        user_answer = transform(message.text[1:])
        correct_answer = user_state[chat_id-1]

        if user_answer == transform(correct_answer):
            bot.reply_to(message, f"Richtig! Die Antwort ist '{correct_answer}'", reply_markup=markup)
            score += 1
        else:
            bot.reply_to(message, f"Falsch! Die Antwort war '{correct_answer}'", reply_markup=markup)
            if score != 0:
                score -= 1

        bot.send_message(message.chat.id, f"Deine Punktzahl ist: {score}")

    chat_id += 1


print("Bot is up!")

bot.infinity_polling()
