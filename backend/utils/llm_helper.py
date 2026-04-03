import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Using gemini-1.5-pro for better nuance in mental health responses.
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
else:
    model = None
    print("WARNING: GEMINI_API_KEY not found in environment. LLM calls will use mock responses.")

async def generate_text_async(prompt: str) -> str:
    """
    Asynchronous generation of text. Uses realistic mock logic if no API key is present.
    """
    if not model:
        # --- Advanced Mock Logic for Testing without API Key ---
        p_lower = prompt.lower()
        
        # Crisis detection mock
        if "detect if user is in crisis" in p_lower:
            keywords = ["suicide", "kill myself", "die", "self-harm", "end it"]
            if any(k in p_lower for k in keywords):
                 return "EMERGENCY: It sounds like you are going through a very difficult time. Please call 988 immediately. You're not alone."
            return "SAFE"

        # Emotion detection mock
        if "determine the primary emotion" in p_lower:
            if "sad" in p_lower or "cry" in p_lower: return "Sadness"
            if "happy" in p_lower or "great" in p_lower: return "Joy"
            if "anxious" in p_lower or "worry" in p_lower: return "Anxiety"
            if "angry" in p_lower or "mad" in p_lower: return "Anger"
            return "Neutral"

        # Therapist response mock
        if "act as a compassionate, professional therapist" in p_lower:
            if "sadness" in p_lower:
                return "I'm so sorry you're feeling this way. It's completely valid to feel sad right now. Can you tell me more about what's been happening?"
            if "joy" in p_lower:
                return "I'm so happy to hear that! It's wonderful to share in these positive moments. What do you think contributed to this good feeling?"
            if "anxiety" in p_lower:
                return "Anxiety can feel very overwhelming. Let's focus on taking a few deep breaths together. What's the biggest thing on your mind right now?"
            return "I hear you. Thank you for sharing that with me. How does it feel to talk about this?"

        return "I'm here to support you. Could you tell me a bit more about how you're feeling today?"

    try:
        # Use the async method from the SDK
        response = await model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "I'm having trouble processing that right now."
