import json
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

class FlightStatus:
    def __init__(self):
        self.load_data()
        self.status_data = {}

    def load_data(self):
        try:
            with open('data/flight_info.json', 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки данных о рейсах: {e}")
            self.data = {"flights": {}, "status_types": {}, "status_icons": {}}

    def get_flight_keyboard(self, user_id: int) -> InlineKeyboardMarkup:
        """Создает клавиатуру с доступными рейсами"""
        keyboard = []
        for flight_id, flight in self.data["flights"].items():
            keyboard.append([
                InlineKeyboardButton(
                    f"{flight_id} | {flight['route']} | {flight['departure_time']}",
                    callback_data=f"flight_{flight_id}"
                )
            ])
        return InlineKeyboardMarkup(keyboard)

    def get_flight_info(self, flight_id: str) -> str:
        """Возвращает информацию о рейсе"""
        if flight_id not in self.data["flights"]:
            return "Рейс не найден"

        flight = self.data["flights"][flight_id]
        status_icon = "🟢"
        for status, icon in self.data["status_icons"].items():
            if status in flight["status"].lower():
                status_icon = icon
                break

        message = f"✈️ Информация о рейсе {flight_id}\n\n"
        message += f"Маршрут: {flight['route']}\n"
        message += f"Авиакомпания: {flight['airline']}\n"
        message += f"Вылет: {flight['departure_time']}\n"
        message += f"Прилет: {flight['arrival_time']}\n"
        message += f"Длительность: {flight['duration']}\n"
        message += f"Самолет: {flight['aircraft']}\n"
        message += f"Статус: {status_icon} {flight['status']}\n"
        message += f"Гейт: {flight['gate']}\n"
        message += f"Терминал: {flight['terminal']}"

        return message

    def handle_callback(self, callback_data: str, user_id: int) -> tuple[str, InlineKeyboardMarkup]:
        """Обрабатывает нажатия на кнопки"""
        if callback_data.startswith("flight_"):
            flight_id = callback_data.split("_")[1]
            return self.get_flight_info(flight_id), None

        return "Ошибка: неверный callback", None 