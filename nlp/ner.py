from natasha import (
    NewsNERTagger,
    NewsEmbedding,
    Doc,
    Segmenter
)

emb = NewsEmbedding()
tagger = NewsNERTagger(emb)
segmenter = Segmenter()

def extract_entities(text):
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_ner(tagger)
    return [(span.text, span.type) for span in doc.spans]