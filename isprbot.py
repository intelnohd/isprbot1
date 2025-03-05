import telebot
import requests
import os
from flask import Flask, request

TOKEN = os.getenv("7294950867:AAHisUZGw7EuAwG6pz-sXflfP99U0IdaoDY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

YANDEX_SPELLER_URL = "https://speller.yandex.net/services/spellservice.json/checkText"

def correct_text(text, lang="uz"):
    params = {"text": text, "lang": lang}
    response = requests.get(YANDEX_SPELLER_URL, params=params)
    corrected_text = text
    for error in response.json():
        word = error["word"]
        replacement = error["s"][0] if error["s"] else word
        corrected_text = corrected_text.replace(word, replacement)
    return corrected_text

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Menga matn yuboring, men xatolarni to'g'irlayman.\n"
                          "Qo'llab-quvvatlanadigan tillar: o'zbek, rus, ingliz.\n"
                          "Tilni o'zgartirish uchun: `/lang en`, `/lang ru`, `/lang uz`")

user_lang = {}

@bot.message_handler(commands=['lang'])
def change_language(message):
    chat_id = message.chat.id
    lang_code = message.text.split()[-1].lower()
    if lang_code in ["ru", "en", "uz"]:
        user_lang[chat_id] = lang_code
        bot.reply_to(message, f"Til {lang_code.upper()} ga o'zgartirildi ✅")
    else:
        bot.reply_to(message, "Qo'llab-quvvatlanadigan tillar: ru (rus), en (ingliz), uz (o'zbek)")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    corrected = correct_text(message.text, lang)
    if corrected == message.text:
        bot.reply_to(message, "✅ Xatolar topilmadi")
    else:
        bot.reply_to(message, f"✍️ To'g'irlangan matn:\n{corrected}")

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
