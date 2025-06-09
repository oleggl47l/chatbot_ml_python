import random
from difflib import SequenceMatcher

def load_dialogues():
    dialogues = []
    current_question = None
    
    print("Начинаю загрузку диалогов из файла...")
    
    with open("data/dialogues.txt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            if current_question is None:
                current_question = line
            else:
                dialogues.append([current_question, line])
                print(f"Загружен диалог: Вопрос: '{current_question}' -> Ответ: '{line}'")
                current_question = None
    
    print(f"Всего загружено диалогов: {len(dialogues)}")
    return dialogues



def find_best_response(user_input, dialogues):
    user_input = user_input.lower().strip("?!.,")
    print(f"\nПоиск ответа для: '{user_input}'")
    
    special_cases = {
        "шутка": "Знаете, почему стюардессы всегда улыбаются? Им платят за то, что они терпят наши шутки! 😄",
        "привет": random.choice(["Привет!", "Здравствуйте!", "Добрый день!"]),
        "пока": random.choice(["До свидания!", "Хорошего дня!", "Удачных полётов!"])
    }

    for word, response in special_cases.items():
        if word in user_input:
            print(f"Найдено совпадение по ключевому слову: '{word}'")
            return response

    best_score = 0.6
    best_response = None
    
    print("Проверяю совпадения в диалогах:")
    for dialogue in dialogues:
        if len(dialogue) == 2:
            input_text, response = dialogue
            input_text = input_text.lower().strip("?!.,")
            
            if user_input == input_text:
                print(f"Найдено точное совпадение: '{input_text}'")
                return response
                
            if input_text in user_input or user_input in input_text:
                score = 0.8
                print(f"Найдено частичное совпадение: '{input_text}' (score: {score})")
            else:
                score = SequenceMatcher(None, user_input, input_text).ratio()
                if score > 0.6:
                    print(f"Найдено похожее совпадение: '{input_text}' (score: {score:.2f})")
            
            if score > best_score:
                best_score = score
                best_response = response

    if best_response:
        print(f"Выбран лучший ответ с score: {best_score:.2f}")
    else:
        print("Подходящий ответ не найден")
    
    return best_response if best_response else "Не совсем понял вопрос. Можете переформулировать?"



class DialogueManager:
    def __init__(self):
        self.context = {}

    def get_response(self, user_input, user_id):
        if user_id in self.context:
            prev_question = self.context[user_id]
            if "билет" in prev_question and "сочи" in user_input.lower():
                self.context.pop(user_id)
                return "Отлично! Вылет в Сочи. Нужен эконом или бизнес класс?"

        response = find_best_response(user_input, load_dialogues())
        self.context[user_id] = user_input
        return response

emotion_responses = {
    "грустно": "Не переживайте! Путешествия - лучшее лекарство от плохого настроения ✈️",
    "рад": "Отлично! Давайте подберём билеты под ваш замечательный настрой! 😊",
    "злюсь": "Понимаю ваше раздражение. Давайте решим проблему вместе."
}


class DialogContext:
    def __init__(self):
        self.context = {}

    def get_context(self, user_id):
        return self.context.get(user_id, {})

    def update_context(self, user_id, key, value):
        if user_id not in self.context:
            self.context[user_id] = {}
        self.context[user_id][key] = value

    def clear_context(self, user_id):
        if user_id in self.context:
            del self.context[user_id]


dialog_context = DialogContext()

def detect_emotion(text):
    text = text.lower()
    if any(word in text for word in ["грустно", "печаль", "тоска"]):
        return "грустно"
    elif any(word in text for word in ["рад", "счастлив", "восторг"]):
        return "рад"
    elif any(word in text for word in ["злюсь", "злость", "бесит"]):
        return "злюсь"
    return None