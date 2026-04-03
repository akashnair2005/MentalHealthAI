from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from collections import Counter

from agents.listener_agent import detect_emotion
from agents.crisis_agent import check_crisis
from agents.therapist_agent import generate_response
from agents.personality_agent import detect_personality

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📊 Mood tracking storage
mood_history = []
MAX_HISTORY = 100  # Keep last 100 messages

@app.get("/")
def home():
    return {"message": "AI Running 🚀"}

@app.post("/chat")
def chat(data: dict):
    user_input = data.get("message", "")

    if check_crisis(user_input):
        return {
            "emotion": "critical",
            "response": "⚠️ Please reach out to someone you trust immediately."
        }

    emotion = detect_emotion(user_input)
    personality = detect_personality(user_input)

    response = generate_response(user_input, emotion, personality)

    # 📊 Track mood
    mood_history.append({
        "emotion": emotion,
        "timestamp": datetime.now().isoformat(),
        "message": user_input[:100]  # Store first 100 chars
    })
    
    # Keep only last MAX_HISTORY entries
    if len(mood_history) > MAX_HISTORY:
        mood_history.pop(0)

    return {
        "emotion": emotion,
        "response": response
    }

@app.get("/mood-stats")
def mood_stats():
    """Get mood statistics for charts"""
    if not mood_history:
        return {
            "total": 0,
            "emotions": {},
            "recent_emotions": [],
            "mood_trend": "neutral"
        }
    
    # Count emotions
    emotion_counts = Counter([m["emotion"] for m in mood_history])
    
    # Calculate percentages
    total = len(mood_history)
    emotion_percentages = {
        emotion: round((count / total) * 100, 2)
        for emotion, count in emotion_counts.items()
    }
    
    # Get recent emotions (last 10)
    recent = [m["emotion"] for m in mood_history[-10:]]
    
    # Determine trend
    recent_emotions = Counter(recent)
    dominant_emotion = recent_emotions.most_common(1)[0][0] if recent_emotions else "neutral"
    
    return {
        "total": total,
        "emotions": dict(emotion_counts),
        "emotion_percentages": emotion_percentages,
        "recent_emotions": recent,
        "dominant_emotion": dominant_emotion,
        "mood_trend": get_mood_trend(recent_emotions)
    }

def get_mood_trend(recent_emotions):
    """Analyze mood trend"""
    positive = recent_emotions.get("happy", 0)
    negative = recent_emotions.get("sad", 0) + recent_emotions.get("angry", 0)
    anxious = recent_emotions.get("anxious", 0) + recent_emotions.get("fear", 0)
    
    if positive > negative and positive > anxious:
        return "improving"
    elif negative > positive:
        return "challenging"
    elif anxious > positive:
        return "stressed"
    else:
        return "stable"