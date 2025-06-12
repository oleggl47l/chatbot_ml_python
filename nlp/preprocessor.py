import re
import warnings

from natasha import Doc, Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger

warnings.filterwarnings("ignore", category=UserWarning, message="pkg_resources is deprecated")

segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)


def preprocess(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)
    text = re.sub(r'\s+', ' ', text)
    return text


def lemmatize(text: str) -> str:
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)

    for token in doc.tokens:
        token.lemmatize(morph_vocab)

    return ' '.join(token.lemma for token in doc.tokens if token.lemma)