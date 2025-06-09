import asyncio
import json
import random
import logging

from telegram.ext import Application, CommandHandler, MessageHandler, filters
from nlp.intent_model import IntentClassifier
from nlp.preprocessor import preprocess, lemmatize
from nlp.ner import extract_city, replace_placeholders
from scenarios.ads import get_random_ad
from scenarios.dialogue_engine import load_dialogues, find_best_response, dialog_context
from utils.spell_check import correct_text
from dotenv import load_dotenv
import os
from data.flight_info import FlightInfo
from nlp.casual_dialog import CasualDialogHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("\n=== Инициализация бота ===")
intent_model = IntentClassifier()
intent_model.train()
print("Модель обучена")

dialogues = load_dialogues()
flight_info = FlightInfo()
print("=== Инициализация завершена ===\n")

class TelegramBot:
    def __init__(self):
        self.intent_classifier = intent_model
        self.casual_handler = CasualDialogHandler()
        self.flight_info = flight_info
        self.dialogues = dialogues
        
    def load_dialogues(self):
        with open('data/dialogues.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_intent_response(self, intent: str, text: str) -> str:
        """Получает ответ для интента с учетом извлеченного города"""
        if intent not in self.intent_classifier.intents:
            return None
            
        city = extract_city(text)
        if city:
            city = self.flight_info.normalize_city(city)
            logger.info(f"Нормализация города: {city}")
            
        responses = self.intent_classifier.intents[intent]['responses']
        response = random.choice(responses)
        
        if '<CITY>' in response and not city:
            return "В какой город вы хотите полететь?"
            
        if city:
            response = replace_placeholders(response, city)
            
        return response

    def handle_message(self, text: str) -> str:
        """Обрабатывает входящее сообщение"""
        logger.info(f"Получено сообщение: {text}")
        
        casual_response, should_add_ad = self.casual_handler.get_response(text)
        if casual_response:
            logger.info("Найден casual диалог")
            return casual_response
            
        intent = self.intent_classifier.predict(text)
        logger.info(f"Определенный интент: {intent}")
        
        if intent:
            response = self.get_intent_response(intent, text)
            if response:
                return response
                
        return random.choice(self.dialogues['fallback_responses'])

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

    city = extract_city(text)
    if city:
        logger.info(f"Извлеченный город: {city}")
        city = flight_info.normalize_city(city)
        logger.info(f"Нормализованный город: {city}")
        
        cleaned = preprocess(text)
        corrected = correct_text(cleaned)
        lemmatized = lemmatize(corrected)
        
        intent = intent_model.predict(lemmatized)
        logger.info(f"Определенный интент: {intent}")

        if intent == "weather_query":
            weather_info = flight_info.format_weather_info(city)
            await update.message.reply_text(weather_info)
            return
        elif intent == "flight_search":
            route_info = flight_info.format_route_info("Москва", city)
            await update.message.reply_text(route_info)
            return
        elif intent == "flight_duration":
            route_info = flight_info.format_route_info("Москва", city)
            await update.message.reply_text(route_info)
            return
        elif intent == "airport_info":
            airport_info = flight_info.format_airport_info(city)
            await update.message.reply_text(airport_info)
            return
        elif intent == "price_query":
            route_info = flight_info.format_route_info("Москва", city)
            await update.message.reply_text(route_info)
            return
        elif intent == "best_time_to_visit":
            weather_info = flight_info.format_weather_info(city)
            await update.message.reply_text(f"Лучшее время для посещения {city}:\n{weather_info}")
            return

    if "парковка" in text.lower() or "стоянка" in text.lower():
        await update.message.reply_text(
            "Информация о парковке в аэропортах:\n"
            "• Краткосрочная парковка: 300₽/час\n"
            "• Долгосрочная парковка: 1000₽/сутки\n"
            "• Бесплатная парковка: первые 15 минут\n"
            "• VIP-парковка: 5000₽/сутки\n\n"
            "Для уточнения информации по конкретному аэропорту, укажите город."
        )
        return

    casual_handler = CasualDialogHandler()
    casual_response, should_add_ad = casual_handler.get_response(text)
    if casual_response:
        logger.info("Найден casual диалог")
        await update.message.reply_text(casual_response)
        return

    response = find_best_response(text, dialogues)
    if response and response != "Не совсем понял вопрос. Можете переформулировать?":
        await update.message.reply_text(response)
        return

    if not city:
        cleaned = preprocess(text)
        corrected = correct_text(cleaned)
        lemmatized = lemmatize(corrected)
        
        intent = intent_model.predict(lemmatized)
        logger.info(f"Определенный интент: {intent}")

        if intent == "greet":
            await update.message.reply_text(random.choice([
                "Привет! Готов помочь с билетами!",
                "Здравствуйте! Куда летим сегодня?"
            ]))
        elif intent == "buy_ticket":
            dialog_context.update_context(user_id, 'awaiting_destination', True)
            await update.message.reply_text("В какой город летим?")
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
        elif intent == "flight_status":
            await update.message.reply_text("Для проверки статуса рейса, пожалуйста, укажите номер рейса или маршрут.")
        elif intent == "luggage_info":
            baggage_info = flight_info.format_baggage_info()
            await update.message.reply_text(baggage_info)
        elif intent == "check_in":
            await update.message.reply_text("Онлайн-регистрация доступна за 24 часа до вылета на сайте авиакомпании или через мобильное приложение.")
        elif intent == "discounts":
            await update.message.reply_text("Сейчас действуют специальные тарифы на рейсы в Сочи и Санкт-Петербург. Уточните конкретный маршрут для получения актуальной информации.")
        elif intent == "business_class":
            baggage_info = flight_info.format_baggage_info("business")
            await update.message.reply_text(baggage_info)
        elif intent == "help":
            await update.message.reply_text("Я могу помочь вам с:\n• Поиском и покупкой билетов\n• Информацией о рейсах и ценах\n• Правилами провоза багажа\n• Онлайн-регистрацией\n• Погодой в городах\nЧто вас интересует?")
        elif intent == "payment_issues":
            await update.message.reply_text("По вопросам оплаты и возврата билетов обращайтесь в службу поддержки авиакомпании или в наш офис.")
        elif intent == "additional_services":
            await update.message.reply_text("Дополнительные услуги включают:\n• Выбор места в салоне\n• Специальное питание\n• Трансфер до аэропорта\n• Страхование\nУточните, какая услуга вас интересует.")
        elif intent == "best_time_to_visit":
            await update.message.reply_text("Для какого города вы хотите узнать лучшее время для посещения?")
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

    application.run_polling()
