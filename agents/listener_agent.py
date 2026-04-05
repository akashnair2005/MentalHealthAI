import pickle
import re
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== ABSOLUTE PATH RESOLUTION FOR RENDER/LINUX ========== 
# Get the absolute path to the project root
CURRENT_FILE = os.path.abspath(__file__) 
AGENTS_DIR = os.path.dirname(CURRENT_FILE)
PROJECT_ROOT = os.path.dirname(AGENTS_DIR)
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "emotion_model.pkl")

# Load the model with error handling
model = None
try:
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        logger.info(f"✅ Model loaded successfully from: {MODEL_PATH}")
    else:
        logger.warning(f"⚠️ Model file not found at: {MODEL_PATH}")
        logger.warning("⚠️ Falling back to keyword-based emotion detection only")
except FileNotFoundError as e:
    logger.error(f"❌ FileNotFoundError: {e}")
    logger.error(f"❌ Could not find model at: {MODEL_PATH}")
except pickle.UnpicklingError as e:
    logger.error(f"❌ Error unpickling model: {e}")
except Exception as e:
    logger.error(f"❌ Unexpected error loading model: {e}")

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
    """Detect emotion from text using keywords and trained model"""
    try:
        text_lower = text.lower()
        
        # Keyword-based detection (priority)
        for emotion, keywords in EMOTION_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                return emotion
        
        # Fall back to trained model if available
        if model is not None:
            cleaned = clean_text(text)
            predicted = model.predict([cleaned])[0]
            
            # If model predicts something, use it
            if predicted and predicted != "neutral":
                return predicted
        
        return "neutral"
    except Exception as e:
        logger.error(f"Error in detect_emotion: {e}")
        return "neutral"