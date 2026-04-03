def suggest_action(emotion):
    suggestions = {
        "sad": "Try deep breathing for 2 minutes 🧘",
        "angry": "Take a short walk 🚶",
        "happy": "Keep doing what makes you happy 😊",
        "fear": "Write your thoughts in a journal 📓",
        "neutral": "Maybe listen to some calming music 🎧"
    }
    
    return suggestions.get(emotion, "Take care of yourself 💙")