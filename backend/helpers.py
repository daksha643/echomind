import whisper
import spacy
from backend import config

# Load the models once and reuse. Loading them on every request
# would make each upload take a minute. This way it's fast after the first time.

_whisper_model = None
_nlp = None


def _get_whisper():
    global _whisper_model
    if _whisper_model is None:
        print("Loading Whisper model... (only happens once)")
        _whisper_model = whisper.load_model(config.WHISPER_SIZE)
    return _whisper_model


def _get_nlp():
    global _nlp
    if _nlp is None:
        print("Loading spaCy model... (only happens once)")
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def speech_to_text(audio_path):
    """Turn a wav file into text using Whisper."""
    result = _get_whisper().transcribe(audio_path)
    return result["text"].strip()


# spaCy labels we care about. Anything else is ignored.
_KEEP_LABELS = {
    "PERSON": "person",
    "GPE": "place",       # countries, cities, states
    "LOC": "place",       # mountains, water bodies
    "FAC": "place",       # buildings, airports
    "DATE": "time",
    "EVENT": "event",
    "ORG": "group",       # companies, organizations
}


def find_entities(text):
    """
    Look through a sentence and pull out people, places, dates.
    Returns a list of dicts like {"name": "Meera", "kind": "person"}.
    """
    doc = _get_nlp()(text)
    found = []
    seen = set()

    for ent in doc.ents:
        kind = _KEEP_LABELS.get(ent.label_)
        if not kind:
            continue
        key = ent.text.lower()
        if key in seen:
            continue
        seen.add(key)
        found.append({"name": ent.text, "kind": kind})

    return found