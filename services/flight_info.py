import json
from typing import Dict, Optional

import pymorphy2


class FlightInfo:
    def __init__(self):
        with open('data/flight_data.json', 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        self.morph = pymorphy2.MorphAnalyzer()

        self.special_cases = {
            'питер': 'Санкт-Петербург',
            'спб': 'Санкт-Петербург',
            'ленинград': 'Санкт-Петербург'
        }

        self.normalized_cities = {}
        for city in self.data['airports'].keys():
            self.normalized_cities[city.lower()] = city
            parses = self.morph.parse(city.lower())
            for parse in parses:
                for form in parse.lexeme:
                    self.normalized_cities[form.word.lower()] = city

    def normalize_city(self, city: str) -> str:
        """Нормализует название города с помощью pymorphy2"""
        if not city:
            return ""

        print(f"Нормализация города: {city}")

        city_lower = city.lower()

        if city_lower in self.special_cases:
            print(f"Найден специальный случай: {city} -> {self.special_cases[city_lower]}")
            return self.special_cases[city_lower]

        if city_lower in self.normalized_cities:
            print(f"Найдено в словаре нормализованных названий: {city} -> {self.normalized_cities[city_lower]}")
            return self.normalized_cities[city_lower]

        parses = self.morph.parse(city_lower)
        if not parses:
            print(f"Не удалось разобрать слово: {city}")
            return city

        for parse in parses:
            normal_form = parse.normal_form
            if normal_form in self.data['airports']:
                print(f"Найдена нормальная форма: {city} -> {normal_form}")
                return normal_form

            for form in parse.lexeme:
                if form.word in self.data['airports']:
                    print(f"Найдена форма слова: {city} -> {form.word}")
                    return form.word

        print(f"Город не найден: {city}")
        return city

    def get_airport_info(self, city: str) -> Optional[Dict]:
        """Получить информацию об аэропорте города"""
        normalized_city = self.normalize_city(city)
        print(f"Поиск информации об аэропорте: {city} -> {normalized_city}")
        return self.data['airports'].get(normalized_city)

    def get_route_info(self, from_city: str, to_city: str) -> Optional[Dict]:
        """Получить информацию о маршруте между городами"""
        normalized_from = self.normalize_city(from_city)
        normalized_to = self.normalize_city(to_city)

        print(f"Поиск маршрута: {from_city}->{to_city} -> {normalized_from}->{normalized_to}")

        for route in self.data['flight_routes']:
            if route['from'] == normalized_from and route['to'] == normalized_to:
                print(f"Найден прямой маршрут: {normalized_from}->{normalized_to}")
                return route

        for route in self.data['flight_routes']:
            if route['from'] == normalized_to and route['to'] == normalized_from:
                print(f"Найден обратный маршрут: {normalized_to}->{normalized_from}")
                return {
                    'from': normalized_from,
                    'to': normalized_to,
                    'duration': route['duration'],
                    'price_range': route['price_range'],
                    'airlines': route['airlines'],
                    'daily_flights': route['daily_flights']
                }

        print(f"Маршрут не найден: {normalized_from}->{normalized_to}")
        return None

    def get_weather_info(self, city: str) -> Optional[Dict]:
        """Получить информацию о погоде в городе"""
        normalized_city = self.normalize_city(city)
        print(f"Поиск информации о погоде: {city} -> {normalized_city}")
        return self.data['weather_seasons'].get(normalized_city)

    def get_baggage_rules(self, class_type: str = 'economy') -> Optional[Dict]:
        """Получить правила провоза багажа для класса обслуживания"""
        return self.data['baggage_rules'].get(class_type)

    def get_airline_info(self, airline: str) -> Optional[Dict]:
        """Получить информацию об авиакомпании"""
        return self.data['airlines'].get(airline)

    def format_airport_info(self, city: str) -> str:
        """Форматировать информацию об аэропорте"""
        info = self.get_airport_info(city)
        if not info:
            return f"К сожалению, у меня нет информации об аэропортах в городе {city}"

        codes = ", ".join(info['codes'])
        transfer = ", ".join(info['transfer'])
        return (
            f"Аэропорты {city}:\n"
            f"• Коды аэропортов: {codes}\n"
            f"• Способы трансфера: {transfer}\n"
            f"• Количество терминалов: {info['terminals']}\n"
            f"• Парковка: {'доступна' if info['parking'] else 'отсутствует'}"
        )

    def format_route_info(self, from_city: str, to_city: str) -> str:
        """Форматировать информацию о маршруте"""
        info = self.get_route_info(from_city, to_city)
        if not info:
            return f"К сожалению, у меня нет информации о прямых рейсах из {from_city} в {to_city}"

        airlines = ", ".join(info['airlines'])
        return (
            f"Информация о рейсах {from_city} - {to_city}:\n"
            f"• Время в пути: {info['duration']} минут\n"
            f"• Цены: от {info['price_range']['economy']}₽ (эконом) до {info['price_range']['business']}₽ (бизнес)\n"
            f"• Авиакомпании: {airlines}\n"
            f"• Рейсов в день: {info['daily_flights']}"
        )

    def format_weather_info(self, city: str) -> str:
        """Форматировать информацию о погоде"""
        info = self.get_weather_info(city)
        if not info:
            return f"К сожалению, у меня нет информации о погоде в городе {city}"

        return (
            f"Климат в {city}:\n"
            f"• Лучший сезон для посещения: {info['best_season']}\n"
            f"• Температура зимой: {info['winter_temp']}\n"
            f"• Температура летом: {info['summer_temp']}"
        )

    def format_baggage_info(self, class_type: str = 'economy') -> str:
        """Форматировать информацию о багаже"""
        info = self.get_baggage_rules(class_type)
        if not info:
            return f"К сожалению, у меня нет информации о правилах провоза багажа для класса {class_type}"

        return (
            f"Правила провоза багажа ({class_type}):\n"
            f"• Ручная кладь: {info['hand_luggage']}\n"
            f"• Багаж: {info['luggage']}"
        )