import asyncio
import json
import random

from telegram.ext import Application, CommandHandler, MessageHandler, filters
from nlp.intent_model import IntentClassifier
from nlp.preprocessor import preprocess, lemmatize
from scenarios.ads import get_random_ad
from scenarios.dialogue_engine import load_dialogues, find_best_response, dialog_context
from utils.spell_check import correct_text
from dotenv import load_dotenv
import os

intent_model = IntentClassifier()
intent_model.model, intent_model.vectorizer = None, None
print("\n=== Инициализация бота ===")
dialogues = load_dialogues()
print("=== Инициализация завершена ===\n")

def get_joke():
    with open('data/intents.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        for intent in data['intents']:
            if intent['tag'] == 'joke':
                return random.choice(intent['responses'])
    return "Извините, у меня закончились шутки 😅"

async def start(update, context):
    await update.message.reply_text("Привет! Я помогу тебе найти лучшие авиабилеты ✈️")


async def handle_message(update, context):
    user_id = update.effective_user.id
    text = update.message.text

    response = find_best_response(text, dialogues)
    if response and response != "Не совсем понял вопрос. Можете переформулировать?":
        await update.message.reply_text(response)
        return

    cleaned = preprocess(text)
    corrected = correct_text(cleaned)
    lemmatized = lemmatize(corrected)
    intent = intent_model.predict(lemmatized)

    if intent == "buy_ticket":
        dialog_context.update_context(user_id, 'awaiting_destination', True)
        await update.message.reply_text("В какой город летим?")
    elif intent == "greet":
        await update.message.reply_text(random.choice([
            "Привет! Готов помочь с билетами!",
            "Здравствуйте! Куда летим сегодня?"
        ]))
    elif intent == "price_query":
        await update.message.reply_text("Цена зависит от даты вылета и класса. Уточните, пожалуйста, дату и класс.")
    elif intent == "joke":
        await update.message.reply_text(get_joke())
    elif intent == "thanks":
        await update.message.reply_text(random.choice([
            "Рад помочь!",
            "Пожалуйста, обращайтесь ещё!",
            "Хорошего дня!"
        ]))
    elif intent == "goodbye":
        await update.message.reply_text(random.choice([
            "До встречи!",
            "Удачного дня и хороших перелётов!",
            "Всегда рад помочь!"
        ]))
    else:
        await update.message.reply_text("Не совсем понял вопрос. Можете переформулировать?")

    if random.random() > 0.8:
        await asyncio.sleep(1)
        await update.message.reply_text(get_random_ad())




def run_bot():
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env файле!")

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")

    # Запускаем асинхронно
    application.run_polling()
