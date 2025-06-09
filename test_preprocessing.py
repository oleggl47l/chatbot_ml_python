from nlp.preprocessor import preprocess, lemmatize
from utils.spell_check import correct_text
from nlp.intent_model import IntentClassifier

def test_preprocessing():
    test_phrases = [
        "Расскажи шутку",
        "Пошути",
        "Смешное что-нибудь",
        "Анекдот давай",
        "Привет",
        "Здравствуйте",
        "Добрый день"
    ]
    
    print("\n=== Тестирование предобработки текста ===")
    for phrase in test_phrases:
        print(f"\nОригинальный текст: '{phrase}'")
        
        cleaned = preprocess(phrase)
        print(f"После preprocess: '{cleaned}'")
        
        corrected = correct_text(cleaned)
        print(f"После correct_text: '{corrected}'")
        
        lemmatized = lemmatize(corrected)
        print(f"После lemmatize: '{lemmatized}'")
        
        # Тест без предлогов
        text_without_preps = ' '.join([word for word in lemmatized.split() 
                                     if word not in ['в', 'до', 'на', 'из', 'от']])
        print(f"Без предлогов: '{text_without_preps}'")

def test_model_training():
    print("\n=== Тестирование обучения модели ===")
    classifier = IntentClassifier()
    
    texts, labels = classifier.load_data()
    print(f"\nЗагружено {len(texts)} примеров")
    print(f"Уникальные классы: {set(labels)}")
    
    classifier.train()
    
    test_phrases = [
        "Расскажи шутку",
        "Пошути",
        "Смешное что-нибудь",
        "Анекдот давай"
    ]
    
    print("\n=== Тестирование предсказаний ===")
    for phrase in test_phrases:
        intent = classifier.predict(phrase)
        print(f"\nФраза: '{phrase}'")
        print(f"Предсказанный интент: {intent}")

if __name__ == "__main__":
    test_preprocessing()
    test_model_training() 