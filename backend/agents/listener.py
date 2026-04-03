from backend.utils.llm_helper import generate_text_async

async def detect_emotion(text: str) -> str:
    """
    Uses the LLM as a classifier to detect the primary emotion asynchronously.
    """
    prompt = f"""
    Analyze the following text and determine the primary emotion the user is feeling.
    Respond with ONLY a single word representing the emotion (e.g., Sadness, Anxiety, Joy, Anger, Fear, Neutral).
    
    Text: "{text}"
    Emotion: 
    """
    emotion = await generate_text_async(prompt)
    
    # Clean up standard mock response if there's no API key
    if "mock response" in emotion.lower():
        return "Neutral"
        
    return emotion.strip().capitalize()
