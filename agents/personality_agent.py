def detect_personality(text):
    text = text.lower()
    words = len(text.split())

    if words < 5:
        return "reserved"

    if any(w in text for w in ["hate", "angry"]):
        return "negative"

    if any(w in text for w in ["happy", "excited", "love"]):
        return "positive"

    if words > 15:
        return "expressive"

    return "neutral"