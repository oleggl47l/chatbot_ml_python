import pandas as pd
import os

emo_dict_path = os.path.join(os.path.dirname(__file__), "..", "data", "emo_dict.csv")
emo_df = pd.read_csv(emo_dict_path)
emo_dict = dict(zip(emo_df["слово"], emo_df["оценка"]))


def analyze_sentiment(text: str) -> float:
    words = text.lower().split()
    scores = [float(emo_dict.get(word, 0)) for word in words]
    if not scores:
        return 0.0
    return sum(scores) / len(scores)


def get_sentiment_label(score: float) -> str:
    if score > 0.2:
        return "positive"
    elif score < -0.2:
        return "negative"
    else:
        return "neutral"
