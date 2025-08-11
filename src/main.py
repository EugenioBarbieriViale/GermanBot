from datetime import datetime
import telebot
from telebot import types

with open("../token.txt", "r") as f:
    token = f.read()

token = token.replace("\n", "")
bot = telebot.TeleBot(token, parse_mode=None)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    username = str(message.from_user.username)

    bot.send_message(message.chat.id, f"Herzlich wilkommen @{username}! Bist du bereit, Verben mit den richtigen Präpositionen zu verbinden?", parse_mode="Markdown")
    bot.send_message(message.chat.id, "Schreib /help, um die möglichen Befehlen zu gucken", parse_mode="Markdown")

    d = str(datetime.now())
    with open("../users.txt", "a") as f:
        print(f"{username} has connected - {d}")
        f.write(username + ": " + d + "\n")

print("Bot is up!")

bot.infinity_polling()
