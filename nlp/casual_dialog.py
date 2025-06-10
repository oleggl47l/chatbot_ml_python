import json
import random
from typing import Optional, Tuple

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from nlp.preprocessor import lemmatize


class CasualDialogHandler:
    def __init__(self, data_path: str = "data/casual_dialogues.json"):
        with open(data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        self.patterns_dict = {}
        self.topic_keywords = {}

        for topic, content in self.data['topics'].items():
            for pattern in content['patterns']:
                self.patterns_dict[pattern] = topic

            keywords = set()
            for pattern in content['patterns']:
                keywords.add(pattern)
                keywords.add(lemmatize(pattern))

            if topic == "weather":
                keywords.update(["погода", "погод", "дождь", "снег", "солнце", "жара", "холод", "градус"])
            elif topic == "work":
                keywords.update(["устал", "устала", "усталость", "работа", "работать", "офис", "начальник"])
            elif topic == "travel":
                keywords.update(["отдых", "отдохнуть", "отдыхать", "отпуск", "поездка", "путешествие"])
            elif topic == "food":
                keywords.update(["еда", "есть", "кушать", "голод", "голодный", "вкусно", "вкусный"])
            elif topic == "movies":
                keywords.update(["кино", "фильм", "смотреть", "посмотреть", "кинотеатр", "сериал"])
            elif topic == "sport":
                keywords.update(["спорт", "спортивный", "тренировка", "зал", "фитнес", "бег", "плавание"])
            elif topic == "music":
                keywords.update(["музыка", "песня", "петь", "петь", "концерт", "группа", "исполнитель"])
            elif topic == "books":
                keywords.update(["книга", "читать", "чтение", "литература", "роман", "автор"])

            self.topic_keywords[topic] = keywords

    def find_topic(self, text: str) -> Optional[str]:
        """Находит подходящую тему для текста"""
        lemmatized_text = lemmatize(text.lower())
        words = set(lemmatized_text.split())

        for pattern, topic in self.patterns_dict.items():
            if pattern in lemmatized_text:
                return topic

        best_match = None
        max_matches = 0

        for topic, keywords in self.topic_keywords.items():
            matches = len(words.intersection(keywords))
            if matches > max_matches:
                max_matches = matches
                best_match = topic

        if max_matches >= 1:
            return best_match

        return None

    def get_response(self, text: str) -> Tuple[Optional[str], bool, Optional[InlineKeyboardMarkup]]:
        """
        Возвращает ответ, флаг для рекламы и клавиатуру с кнопкой
        Returns: (response, should_add_ad, keyboard)
        """
        topic = self.find_topic(text)
        if not topic:
            return None, False, None

        responses = self.data['topics'][topic]['responses']
        response = random.choice(responses)

        should_add_ad = random.random() < 0.7
        keyboard = None

        if should_add_ad:
            transition = random.choice(self.data['transition_phrases'])
            transition_text = f"{transition['phrase']} {transition['emoji']}"

            follow_up = random.choice(self.data['follow_ups'])

            ad_phrase = random.choice(self.data['ad_phrases'])

            response = f"{response}\n\n{transition_text}\n{follow_up}\n{ad_phrase}"

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✈️ Заказать билет", callback_data="start_booking")]
            ])

        return response, should_add_ad, keyboard