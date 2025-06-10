import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from services.flight_status import FlightStatus
from services.ticket_booking import TicketBooking

logger = logging.getLogger(__name__)

class ButtonHandler:
    def __init__(self, ticket_booking: TicketBooking, flight_status: FlightStatus):
        self.ticket_booking = ticket_booking
        self.flight_status = flight_status

    def get_menu_keyboard(self) -> ReplyKeyboardMarkup:
        """Создает клавиатуру с основными командами"""
        keyboard = [
            [KeyboardButton("✈️ Бронирование"), KeyboardButton("📊 Статус рейса")],
            [KeyboardButton("❓ Помощь"), KeyboardButton("ℹ️ Информация")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    def get_booking_keyboard(self) -> InlineKeyboardMarkup:
        """Создает клавиатуру для бронирования"""
        keyboard = [
            [InlineKeyboardButton("✈️ Заказать билет", callback_data="start_booking")]
        ]
        return InlineKeyboardMarkup(keyboard)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обрабатывает нажатия на кнопки"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        callback_data = query.data

        if callback_data == "start_booking":
            self.ticket_booking.booking_data[user_id] = {
                "step": "select_destination",
                "data": {}
            }
            message = "✈️ Выберите направление:"
            keyboard = self.ticket_booking.get_booking_keyboard("select_destination", user_id)
            await query.message.reply_text(text=message, reply_markup=keyboard)
            await query.edit_message_reply_markup(reply_markup=None)
            return

        if user_id in self.ticket_booking.booking_data:
            message, keyboard = self.ticket_booking.process_callback(callback_data, user_id)
            if keyboard:
                await query.edit_message_text(text=message, reply_markup=keyboard)
            else:
                await query.edit_message_text(text=message)
            return

        if callback_data.startswith("flight_"):
            message, keyboard = self.flight_status.handle_callback(callback_data, user_id)
            if keyboard:
                await query.edit_message_text(text=message, reply_markup=keyboard)
            else:
                await query.edit_message_text(text=message)
            return

        await query.edit_message_text(text="Ошибка: неверный callback") 