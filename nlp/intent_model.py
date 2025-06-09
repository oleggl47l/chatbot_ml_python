import json
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from nlp.preprocessor import preprocess, lemmatize
from utils.spell_check import correct_text

class IntentClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=3000,
            ngram_range=(1, 3),
            min_df=1,
            max_df=0.9,
            token_pattern=r'(?u)\b\w+\b'
        )
        self.model = LogisticRegression(
            C=2.0,
            max_iter=2000,
            class_weight='balanced',
            solver='saga',
            multi_class='multinomial',
            tol=1e-3
        )
        self.label_encoder = LabelEncoder()
        self.confidence_threshold = 0.2

    def load_data(self, path='data/intents.json'):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        texts = []
        labels = []

        for intent in data["intents"]:
            tag = intent["tag"]
            for pattern in intent["patterns"]:
                texts.append(pattern)
                labels.append(tag)
                
                cleaned = preprocess(pattern)
                corrected = correct_text(cleaned)
                lemmatized = lemmatize(corrected)
                
                if lemmatized != pattern:
                    texts.append(lemmatized)
                    labels.append(tag)
                
                text_without_preps = ' '.join([word for word in lemmatized.split()
                                             if word not in ['в', 'до', 'на', 'из', 'от']])
                if text_without_preps != lemmatized:
                    texts.append(text_without_preps)
                    labels.append(tag)
                
                if '<CITY>' in pattern:
                    for city in ['Москва', 'Санкт-Петербург', 'Сочи', 'Владивосток']:
                        city_pattern = pattern.replace('<CITY>', city)
                        texts.append(city_pattern)
                        labels.append(tag)
                        
                        cleaned = preprocess(city_pattern)
                        corrected = correct_text(cleaned)
                        lemmatized = lemmatize(corrected)
                        texts.append(lemmatized)
                        labels.append(tag)

        print(f"\nЗагружено {len(texts)} примеров для обучения")
        print(f"Уникальные классы: {set(labels)}")
        return texts, labels

    def train(self):
        print("\n=== Начало обучения модели ===")
        texts, labels = self.load_data()
        
        self.label_encoder.fit(labels)
        y = self.label_encoder.transform(labels)
        
        x = self.vectorizer.fit_transform(texts)
        print(f"Размерность признаков: {x.shape}")
        
        self.model.fit(x, y)
        
        train_predictions = self.model.predict(x)
        train_accuracy = np.mean(train_predictions == y)
        print(f"Точность на обучающей выборке: {train_accuracy:.2f}")
        
        print("\nПримеры предсказаний:")
        for i in range(min(5, len(texts))):
            pred = self.model.predict(x[i:i+1])[0]
            prob = self.model.predict_proba(x[i:i+1])[0]
            pred_class = self.label_encoder.inverse_transform([pred])[0]
            print(f"Текст: '{texts[i]}'")
            print(f"Предсказанный класс: {pred_class}")
            print(f"Уверенность: {prob[pred]:.2f}")
            print("---")
        
        joblib.dump((self.vectorizer, self.model, self.label_encoder), 'model/intent_model.pkl')
        print("=== Обучение завершено ===\n")

    def predict(self, text):
        if not hasattr(self, 'model') or not hasattr(self, 'vectorizer'):
            try:
                self.vectorizer, self.model, self.label_encoder = joblib.load('model/intent_model.pkl')
            except:
                print("Ошибка загрузки модели, выполняем обучение...")
                self.train()
        
        texts_to_predict = [text]
        
        cleaned = preprocess(text)
        corrected = correct_text(cleaned)
        lemmatized = lemmatize(corrected)
        
        if lemmatized != text:
            texts_to_predict.append(lemmatized)
        
        text_without_preps = ' '.join([word for word in lemmatized.split() 
                                     if word not in ['в', 'до', 'на', 'из', 'от']])
        if text_without_preps != lemmatized:
            texts_to_predict.append(text_without_preps)
        
        best_prob = 0
        best_intent = None
        
        for text_to_predict in texts_to_predict:
            x = self.vectorizer.transform([text_to_predict])
            probabilities = self.model.predict_proba(x)[0]
            
            max_prob_idx = np.argmax(probabilities)
            max_prob = probabilities[max_prob_idx]
            
            if max_prob > best_prob:
                best_prob = max_prob
                best_intent = self.label_encoder.inverse_transform([max_prob_idx])[0]
        
        print(f"\nАнализ текста: '{text}'")
        print(f"Варианты текста для анализа:")
        for t in texts_to_predict:
            print(f"- '{t}'")
        print(f"Предсказанный класс: {best_intent}")
        print(f"Уверенность: {best_prob:.2f}")
        
        if best_prob < self.confidence_threshold:
            print("Уверенность ниже порога, возвращаем None")
            return None
            
        return best_intent

    def update_model(self, new_text, new_intent):
        if not self.model or not self.vectorizer:
            self.vectorizer, self.model, self.label_encoder = joblib.load('model/intent_model.pkl')
        
        cleaned = preprocess(new_text)
        corrected = correct_text(cleaned)
        lemmatized = lemmatize(corrected)
        
        x = self.vectorizer.transform([lemmatized])
        y = self.label_encoder.transform([new_intent])
        
        self.model.partial_fit(x, y, classes=self.label_encoder.classes_)
        
        joblib.dump((self.vectorizer, self.model, self.label_encoder), 'model/intent_model.pkl')
