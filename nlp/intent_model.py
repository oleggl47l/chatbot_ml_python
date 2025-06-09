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
            max_features=1000,
            ngram_range=(1, 2),
            min_df=2
        )
        self.model = LogisticRegression(
            C=1.0,
            max_iter=1000,
            class_weight='balanced'
        )
        self.label_encoder = LabelEncoder()
        self.confidence_threshold = 0.6

    def load_data(self, path='data/intents.json'):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        texts = []
        labels = []

        for intent in data["intents"]:
            tag = intent["tag"]
            for pattern in intent["patterns"]:
                cleaned = preprocess(pattern)
                corrected = correct_text(cleaned)
                lemmatized = lemmatize(corrected)
                texts.append(lemmatized)
                labels.append(tag)

        return texts, labels

    def train(self):
        texts, labels = self.load_data()
        
        self.label_encoder.fit(labels)
        y = self.label_encoder.transform(labels)
        
        x = self.vectorizer.fit_transform(texts)
        
        self.model.fit(x, y)
        
        joblib.dump((self.vectorizer, self.model, self.label_encoder), 'model/intent_model.pkl')
        
        train_predictions = self.model.predict(x)
        train_accuracy = np.mean(train_predictions == y)
        print(f"Точность на обучающей выборке: {train_accuracy:.2f}")

    def predict(self, text):
        if not self.model or not self.vectorizer:
            self.vectorizer, self.model, self.label_encoder = joblib.load('model/intent_model.pkl')
        
        cleaned = preprocess(text)
        corrected = correct_text(cleaned)
        lemmatized = lemmatize(corrected)
        
        x = self.vectorizer.transform([lemmatized])
        probabilities = self.model.predict_proba(x)[0]
        
        max_prob_idx = np.argmax(probabilities)
        max_prob = probabilities[max_prob_idx]
        
        if max_prob < self.confidence_threshold:
            return None
            
        predicted_class = self.label_encoder.inverse_transform([max_prob_idx])[0]
        
        return predicted_class

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
