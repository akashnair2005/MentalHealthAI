def get_action_suggestions(emotion: str) -> list[str]:
    \"\"\"
    Provides actionable suggestions based on the detected emotion.
    \"\"\"
    emotion = emotion.lower()
    
    suggestions_map = {
        "anxiety": [
            "Try the 4-7-8 breathing technique.",
            "Ground yourself: Name 5 things you can see.",
            "Take a short walk outside."
        ],
        "sadness": [
            "Write down your feelings in a journal.",
            "Listen to your favorite calming music.",
            "Reach out to a friend or loved one."
        ],
        "anger": [
            "Take 10 deep breaths.",
            "Do a quick physical activity, like jumping jacks.",
            "Write down what made you angry, then rip it up."
        ],
        "stress": [
            "Take a 5-minute break away from screens.",
            "Do a progressive muscle relaxation exercise.",
            "Drink a glass of water."
        ],
        "joy": [
            "Write down what made you happy to remember it.",
            "Share your good mood with someone else.",
            "Channel your energy into a creative hobby."
        ],
        "fear": [
            "Remind yourself that you are safe in this moment.",
            "Focus on a comforting object nearby.",
            "Practice box breathing."
        ]
    }
    
    # Default fallback
    return suggestions_map.get(emotion, [
        "Take a deep breath and relax your shoulders.",
        "Take a moment to check in with your body.",
        "Drink some water and stay hydrated."
    ])
