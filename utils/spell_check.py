from spellchecker import SpellChecker

spell = SpellChecker(language='ru')

def correct_text(text):
    words = text.split()
    corrected = [spell.correction(word) if word in spell else word for word in words]
    return ' '.join(corrected)