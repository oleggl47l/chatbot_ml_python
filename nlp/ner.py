from typing import Optional, List, Dict

from natasha import (
    NewsNERTagger,
    NewsEmbedding,
    Doc,
    Segmenter,
    MorphVocab
)

emb = NewsEmbedding()
tagger = NewsNERTagger(emb)
segmenter = Segmenter()
morph_vocab = MorphVocab()


def normalize_city(city):
    """
    Нормализует название города
    """
    if not city:
        return None
    
    return city.capitalize()

def extract_entities(text: str) -> List[Dict[str, str]]:
    """Извлекает именованные сущности из текста"""
    words = text.split()
    capitalized_words = [word.capitalize() for word in words]
    processed_text = ' '.join(capitalized_words)
    
    doc = Doc(processed_text)
    doc.segment(segmenter)
    doc.tag_ner(tagger)
    
    entities = []
    for span in doc.spans:
        if span.type == 'LOC':
            span.normalize(morph_vocab)
            entities.append({
                'text': span.text,
                'type': span.type,
                'normalized': span.normal
            })
    
    print(f"Извлеченные сущности: {entities}")
    return entities

def extract_city(text: str) -> Optional[str]:
    """Извлекает название города из текста"""
    entities = extract_entities(text)
    
    for entity in entities:
        if entity['type'] == 'LOC':
            return entity['normalized']
    
    return None

def replace_placeholders(text, city=None):
    """
    Заменяет плейсхолдеры в тексте на реальные значения
    """
    if city:
        text = text.replace('<CITY>', city)
        print(f"Заменен плейсхолдер на город: {city}")
    return text