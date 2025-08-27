import re
import string 
import spacy 

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise OSError(
        "spaCy 'en_core_web_sm' model not found."
        "Run: python -m spacy download en_core_web_sm"
    )

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)

    text = text.lower()
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)

    text = text.translate(str.maketrans("", "", string.punctuation + string.digits))
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tockenize_and_lemmatize(text: str) -> str:
    doc = nlp(text)
    tokens = [
        token.lemma_ for token in doc
        if not token.is_stop and not token.is_punct and token.is_alpha
    ]
    return tokens

def preprocess_text(text: str) -> list[str]:
    cleaned = clean_text(text)
    tokens = tockenize_and_lemmatize(cleaned)
    return "".join(tokens)
