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

def extract_entities(text):
    """
    Извлекает именованные сущности из текста
    """
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_ner(tagger)
    
    for span in doc.spans:
        span.normalize(morph_vocab)
    
    entities = [(span.normal, span.type) for span in doc.spans]
    print(f"Извлеченные сущности: {entities}")
    return entities

def extract_city(text):
    """
    Извлекает название города из текста
    """
    entities = extract_entities(text)
    for entity, type_ in entities:
        if type_ == 'LOC':
            normalized_city = normalize_city(entity)
            print(f"Найден город через NER: {entity} -> {normalized_city}")
            return normalized_city
    
    words = text.lower().split()
    for i, word in enumerate(words):
        if word in ['в', 'до', 'на'] and i + 1 < len(words):
            potential_city = words[i + 1]
            if potential_city not in ['и', 'или', 'но', 'а', 'да']:
                normalized_city = normalize_city(potential_city)
                print(f"Найден город по ключевым словам: {potential_city} -> {normalized_city}")
                return normalized_city
    
    print("Город не найден")
    return None

def replace_placeholders(text, city=None):
    """
    Заменяет плейсхолдеры в тексте на реальные значения
    """
    if city:
        text = text.replace('<CITY>', city)
        print(f"Заменен плейсхолдер на город: {city}")
    return text