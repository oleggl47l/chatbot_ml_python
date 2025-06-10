import json
import logging
from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

class TicketBooking:
    def __init__(self):
        self.load_data()
        self.booking_data = {}

    def load_data(self):
        """Загружает данные из JSON файла"""
        try:
            with open('data/ticket_data.json', 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            self.data = {}

    def get_booking_keyboard(self, step, user_id):
        """Возвращает клавиатуру для текущего шага бронирования"""
        if step == "select_destination":
            return self._get_destination_keyboard()
        elif step == "select_date":
            return self._get_date_keyboard()
        elif step == "select_class":
            return self._get_class_keyboard()
        elif step == "select_seat":
            return self._get_seat_keyboard()
        elif step == "select_meal":
            return self._get_meal_keyboard()
        elif step == "payment":
            return self._get_payment_keyboard()
        return None

    def _get_destination_keyboard(self):
        """Клавиатура выбора направления"""
        keyboard = [
            [InlineKeyboardButton("Москва → Санкт-Петербург", callback_data="route_MOW-LED")],
            [InlineKeyboardButton("Москва → Сочи", callback_data="route_MOW-AER")],
            [InlineKeyboardButton("Москва → Казань", callback_data="route_MOW-KZN")],
            [InlineKeyboardButton("Москва → Екатеринбург", callback_data="route_MOW-SVX")],
            [InlineKeyboardButton("Москва → Новосибирск", callback_data="route_MOW-OVB")]
        ]
        return InlineKeyboardMarkup(keyboard)

    def _get_date_keyboard(self):
        """Клавиатура выбора даты"""
        keyboard = []
        today = datetime.now()
        
        for i in range(7):
            date = today + timedelta(days=i)
            date_str = date.strftime("%d.%m.%Y")
            callback_data = f"date_{date.strftime('%Y-%m-%d')}"
            keyboard.append([InlineKeyboardButton(date_str, callback_data=callback_data)])
            
        return InlineKeyboardMarkup(keyboard)

    def _get_class_keyboard(self):
        """Клавиатура выбора класса"""
        keyboard = []
        for class_id, class_info in self.data["flight_classes"].items():
            button_text = f"{class_info['name']} - {class_info['description']}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"class_{class_id}")])
        return InlineKeyboardMarkup(keyboard)

    def _get_seat_keyboard(self):
        """Клавиатура выбора места"""
        keyboard = []
        for seat_id, seat_info in self.data["seat_types"].items():
            button_text = f"{seat_info['name']} - {seat_info['description']}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"seat_{seat_id}")])
        return InlineKeyboardMarkup(keyboard)

    def _get_meal_keyboard(self):
        """Клавиатура выбора питания"""
        keyboard = []
        for meal_id, meal_info in self.data["meal_options"].items():
            button_text = f"{meal_info['name']} - {meal_info['description']}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"meal_{meal_id}")])
        return InlineKeyboardMarkup(keyboard)

    def _get_payment_keyboard(self):
        """Клавиатура выбора способа оплаты"""
        keyboard = []
        for payment_id, payment_info in self.data["payment_methods"].items():
            button_text = f"{payment_info['name']} - {payment_info['description']}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"payment_{payment_id}")])
        return InlineKeyboardMarkup(keyboard)

    def get_step_message(self, step):
        """Возвращает сообщение для текущего шага"""
        if step in self.data["booking_steps"]:
            step_info = self.data["booking_steps"][step]
            return f"{step_info['name']}\n{step_info['description']}"
        return "Выберите опцию:"

    def start_booking(self, user_id):
        """Начинает процесс бронирования для пользователя"""
        self.booking_data[user_id] = {
            "step": "select_destination",
            "data": {}
        }
        return self.get_step_message("select_destination"), self.get_booking_keyboard("select_destination", user_id)

    def process_callback(self, user_id, callback_data):
        """Обрабатывает callback от кнопок"""
        if user_id not in self.booking_data:
            return "Ошибка: сессия бронирования не найдена", None

        booking = self.booking_data[user_id]
        current_step = booking["step"]

        if current_step == "select_destination" and callback_data.startswith("route_"):
            route = callback_data.split("_")[1]
            booking["data"]["route"] = route
            booking["step"] = "select_date"
            return self.get_step_message("select_date"), self.get_booking_keyboard("select_date", user_id)

        elif current_step == "select_date" and callback_data.startswith("date_"):
            date = callback_data.split("_")[1]
            booking["data"]["date"] = date
            booking["step"] = "select_class"
            return self.get_step_message("select_class"), self.get_booking_keyboard("select_class", user_id)

        elif current_step == "select_class" and callback_data.startswith("class_"):
            class_id = callback_data.split("_")[1]
            booking["data"]["class"] = class_id
            booking["step"] = "select_seat"
            return self.get_step_message("select_seat"), self.get_booking_keyboard("select_seat", user_id)

        elif current_step == "select_seat" and callback_data.startswith("seat_"):
            seat_id = callback_data.split("_")[1]
            booking["data"]["seat"] = seat_id
            booking["step"] = "select_meal"
            return self.get_step_message("select_meal"), self.get_booking_keyboard("select_meal", user_id)

        elif current_step == "select_meal" and callback_data.startswith("meal_"):
            meal_id = callback_data.split("_")[1]
            booking["data"]["meal"] = meal_id
            booking["step"] = "enter_passenger"
            return "Пожалуйста, введите данные пассажира в формате:\nФамилия Имя Отчество\nДата рождения (ДД.ММ.ГГГГ)\nСерия и номер паспорта", None

        elif current_step == "payment" and callback_data.startswith("payment_"):
            payment_id = callback_data.split("_")[1]
            booking["data"]["payment"] = payment_id
            return self._complete_booking(user_id), None

        return "Неизвестная команда", None

    def process_passenger_data(self, user_id, text):
        """Обрабатывает введенные данные пассажира"""
        if user_id not in self.booking_data:
            return "Ошибка: сессия бронирования не найдена", None

        booking = self.booking_data[user_id]
        if booking["step"] != "enter_passenger":
            return "Ошибка: неверный шаг бронирования", None

        try:
            lines = text.strip().split('\n')
            if len(lines) != 3:
                return "Пожалуйста, введите данные в правильном формате:\nФамилия Имя Отчество\nДата рождения (ДД.ММ.ГГГГ)\nСерия и номер паспорта", None

            booking["data"]["passenger"] = {
                "full_name": lines[0],
                "birth_date": lines[1],
                "passport": lines[2]
            }
            booking["step"] = "payment"
            return self.get_step_message("payment"), self.get_booking_keyboard("payment", user_id)

        except Exception as e:
            logger.error(f"Ошибка обработки данных пассажира: {e}")
            return "Ошибка в формате данных. Пожалуйста, проверьте и введите снова", None

    def _complete_booking(self, user_id):
        """Завершает процесс бронирования"""
        if user_id not in self.booking_data:
            return "Ошибка: сессия бронирования не найдена"

        booking = self.booking_data[user_id]
        data = booking["data"]

        message = "🎫 Бронирование завершено!\n\n"
        message += f"Маршрут: {data['route']}\n"
        message += f"Дата: {data['date']}\n"
        message += f"Класс: {self.data['flight_classes'][data['class']]['name']}\n"
        message += f"Место: {self.data['seat_types'][data['seat']]['name']}\n"
        message += f"Питание: {self.data['meal_options'][data['meal']]['name']}\n"
        message += f"Пассажир: {data['passenger']['full_name']}\n"
        message += f"Способ оплаты: {self.data['payment_methods'][data['payment']]['name']}\n\n"
        message += "Спасибо за бронирование! Ваш билет будет отправлен на указанный email."

        del self.booking_data[user_id]

        return message 