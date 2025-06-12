import logging

from telegram import Update
from telegram.ext import ContextTypes

from handlers.buttons import ButtonHandler
from services.flight_info import FlightInfo
from services.flight_status import FlightStatus
from services.ticket_booking import TicketBooking

logger = logging.getLogger(__name__)

class CommandHandler:
    def __init__(self, flight_info: FlightInfo, flight_status: FlightStatus, 
                 ticket_booking: TicketBooking, button_handler: ButtonHandler):
        self.flight_info = flight_info
        self.flight_status = flight_status
        self.ticket_booking = ticket_booking
        self.button_handler = button_handler

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает команду /start"""
        keyboard = self.button_handler.get_menu_keyboard()
        await update.message.reply_text(
            "Привет! Я бот для поиска авиабилетов и информации о рейсах. "
            "Чем могу помочь?",
            reply_markup=keyboard
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает команду /help"""
        help_text = (
            "Я могу помочь вам с:\n\n"
            "🔍 Поиском авиабилетов\n"
            "✈️ Информацией о рейсах\n"
            "🌤 Прогнозом погоды\n"
            "🎫 Бронированием билетов\n\n"
            "Просто напишите, что вас интересует, например:\n"
            "- Какие рейсы есть в Москву?\n"
            "- Сколько лететь до Парижа?\n"
            "- Какая погода в Лондоне?\n"
            "- Хочу купить билет в Берлин"
        )
        await update.message.reply_text(help_text)

    async def book_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает команду /book"""
        keyboard = self.button_handler.get_booking_keyboard()
        await update.message.reply_text(
            "Давайте подберем для вас билет. Выберите город назначения:",
            reply_markup=keyboard
        ) 