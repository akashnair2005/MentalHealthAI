import pickle
import re

with open("models/emotion_model.pkl", "rb") as f:
    model = pickle.load(f)

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return text

# Emotion keywords for better detection
EMOTION_KEYWORDS = {
    "sad": ["sad", "depressed", "down", "unhappy", "miserable", "blue", "grief", "heartbroken", "lonely", "loss", "miss"],
    "angry": ["angry", "mad", "furious", "rage", "annoyed", "frustrated", "upset", "irritated", "hate"],
    "anxious": ["anxious", "worried", "nervous", "stressed", "stress", "panic", "afraid", "scared", "fear", "dread", "tense"],
    "happy": ["happy", "glad", "joyful", "excited", "great", "wonderful", "amazing", "love", "blessed", "grateful"],
    "fear": ["fear", "afraid", "scared", "terrified", "panic", "nightmare", "anxiety", "dread"],
}

def detect_emotion(text):
    try:
        text_lower = text.lower()
        
        # Keyword-based detection (priority)
        for emotion, keywords in EMOTION_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                return emotion
        
        # Fall back to trained model
        cleaned = clean_text(text)
        predicted = model.predict([cleaned])[0]
        
        # If model predicts something, use it
        if predicted and predicted != "neutral":
            return predicted
        
        return "neutral"
    except:
        return "neutral"