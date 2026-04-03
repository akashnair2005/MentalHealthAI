from collections import Counter
from backend.agents.memory import get_mood_history

async def analyze_mood_trends(user_id: str) -> str:
    """
    Analyzes recent mood history to return a trend overview asynchronously.
    """
    history = await get_mood_history(user_id, limit=20)
    
    if not history:
        return "No recent mood data to analyze."
        
    emotions = [entry["emotion"] for entry in history if entry["emotion"]]
    if not emotions:
        return "No recent mood data to analyze."
        
    counts = Counter(emotions)
    most_common = counts.most_common(1)[0][0]
    
    total = len(emotions)
    most_common_percent = (counts[most_common] / total) * 100
    
    # Formulate a simple insight
    if "EMERGENCY" in most_common.upper() or most_common.lower() in ["fear", "anxiety", "sadness", "anger", "stress"]:
        if most_common_percent > 60:
            return f"You've been feeling predominantly '{most_common}' lately ({int(most_common_percent)}%). It's important to keep using your coping strategies."
        else:
            return f"Your feelings are mixed, but '{most_common}' is somewhat common right now."
    else:
        if most_common_percent > 60:
            return f"Your predominant mood recently has been '{most_common}' ({int(most_common_percent)}%). That's a strong trend!"
        else:
            return f"You've had a balanced mix of emotions recently, with '{most_common}' appearing slightly more often."
