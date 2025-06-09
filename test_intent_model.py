from nlp.intent_model import IntentClassifier
from nlp.preprocessor import preprocess, lemmatize
from nlp.ner import extract_city, replace_placeholders
from utils.spell_check import correct_text

def test_model():
    classifier = IntentClassifier()
    classifier.train()
    
    test_phrases = [
        "Привет, как дела?",
        "Хочу купить билет в Москву",
        "Сколько стоит перелет в Сочи?",
        "Спасибо за помощь",
        "Расскажи шутку",
        "Пока, до свидания",
        "Какая погода в Москве?",
        "Рейсы в Санкт-Петербург",
        "Какие есть рейсы до Казани",
        "Найти билеты в Новосибирск",
        "Расписание в Москву",
        "Самолёты в Сочи",
        "рейсы в <CITY>",
    ]
    
    print("\n=== Тестирование модели ===")
    for phrase in test_phrases:
        print("\n" + "="*50)
        print(f"Тестируем фразу: '{phrase}'")
        
        cleaned = preprocess(phrase)
        corrected = correct_text(cleaned)
        lemmatized = lemmatize(corrected)
        print(f"После предобработки: '{lemmatized}'")
        
        city = extract_city(phrase)
        if city:
            print(f"Извлеченный город: {city}")
        
        intent = classifier.predict(lemmatized)
        print(f"Предсказанный интент: {intent}")
        
        if intent == "flight_search" and city:
            response = replace_placeholders("Ищу рейсы в <CITY>...", city)
            print(f"Ответ с городом: {response}")

if __name__ == "__main__":
    test_model() 