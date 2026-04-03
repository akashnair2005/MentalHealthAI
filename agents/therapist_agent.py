from transformers import pipeline
import threading

# 🔥 Lazy load TinyLlama (loads on first use, not on import)
generator = None
model_loaded = False
model_loading = False
chat_history = []

# Background model loader
def _load_model_async():
    """Load model in background thread"""
    global generator, model_loaded, model_loading
    if model_loading or model_loaded:
        return
    
    model_loading = True
    try:
        print("🔄 Loading TinyLlama model (background)...")
        generator = pipeline(
            "text-generation",
            model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            device=-1  # Use CPU
        )
        model_loaded = True
        print("✅ TinyLlama loaded successfully!")
    except Exception as e:
        print(f"⚠️ Model loading error: {e}")
        model_loaded = True
    finally:
        model_loading = False

# 🔹 Emotion-specific prompting strategies
EMOTION_PROMPTS = {
    "sad": """You are a compassionate therapist. The user is feeling sad. 
Respond with warmth and empathy. Validate their feelings first, then ask a gentle follow-up question.
Keep your response 2-3 sentences. Be conversational and human-like.""",
    
    "angry": """You are a calm and understanding therapist. The user is feeling angry or frustrated.
Acknowledge their frustration without judgment. Help them explore what's beneath the anger.
Ask a thoughtful question to help them express themselves. Keep it brief (2-3 sentences).""",
    
    "anxious": """You are a reassuring therapist. The user is feeling anxious or stressed.
Provide comfort and grounding. Use simple, calming language. Suggest a simple coping strategy.
Keep your response short (2-3 sentences) and supportive.""",
    
    "fear": """You are a protective and supportive therapist. The user is experiencing fear.
Validate their fear without minimizing it. Help them feel safe to talk about what they fear.
Ask what specifically is worrying them. Keep it brief and gentle.""",
    
    "happy": """You are an encouraging therapist. The user is feeling happy or positive.
Celebrate their joy with them! Ask what's making them happy. Encourage them to savor this moment.
Keep it enthusiastic but genuine (2-3 sentences).""",
    
    "neutral": """You are an attentive therapist. The user is sharing something neutral.
Show genuine interest and curiosity. Ask an open-ended question to help them explore deeper.
Be warm and encouraging. Keep it brief (2-3 sentences)."""
}

# 🔹 Fallback responses for quick processing
FALLBACK = {
    "sad": "I can hear that you're going through something difficult. I'm here for you. What's weighing on your heart right now?",
    "angry": "It sounds like something has really upset you. That's understandable. Would you like to tell me more about what happened?",
    "happy": "That's wonderful to hear! I'm glad you're feeling good. What made your day better?",
    "fear": "It's okay to feel scared. Many people experience fear. What specifically is worrying you?",
    "anxious": "I understand that you're worried about something. Let's talk through it together. What's on your mind?",
    "neutral": "I'm listening. Tell me more about what's going on."
}

def _get_emotion_prompt(emotion, text):
    """Get appropriate prompt based on emotion"""
    base_prompt = EMOTION_PROMPTS.get(emotion, EMOTION_PROMPTS["neutral"])
    
    return f"""{base_prompt}

User's message: "{text}"

Your response:"""

def _clean_response(response_text):
    """Clean and format AI response for human readability"""
    # Remove model repetition and keep only the response
    if "Your response:" in response_text:
        response_text = response_text.split("Your response:")[-1].strip()
    
    # Remove leading unnecessary phrases
    response_text = response_text.strip()
    
    # Ensure proper punctuation
    if response_text and not response_text[-1] in '.!?':
        response_text += '.'
    
    return response_text

def generate_response(text, emotion, personality):
    """Generate empathetic therapeutic response using TinyLlama"""
    global generator, model_loaded
    
    # Start background model loading if not already started
    if not model_loaded and not model_loading:
        thread = threading.Thread(target=_load_model_async, daemon=True)
        thread.start()
    
    # ⚡ Very short input → always use fallback (faster)
    if len(text.split()) < 3:
        return FALLBACK.get(emotion, FALLBACK["neutral"])

    # If model not ready yet, use fallback with enhanced responses
    if not model_loaded or generator is None:
        enhanced_fallback = get_enhanced_fallback(text, emotion)
        return enhanced_fallback

    try:
        # Get emotion-specific prompt
        prompt = _get_emotion_prompt(emotion, text)

        # Generate response with timeout handling
        output = generator(
            prompt,
            max_length=200,
            do_sample=True,
            temperature=0.8,
            top_p=0.95,
            top_k=50
        )[0]["generated_text"]

        # Clean response
        response = _clean_response(output)
        
        # Ensure response is not too long (2-3 sentences max)
        sentences = response.split('. ')
        if len(sentences) > 3:
            response = '. '.join(sentences[:3]) + '.'
        
        chat_history.append({
            'user': text,
            'emotion': emotion,
            'response': response
        })

        return response if response.strip() else FALLBACK.get(emotion, FALLBACK["neutral"])

    except Exception as e:
        print(f"⚠️ Generation error: {e}")
        return FALLBACK.get(emotion, FALLBACK["neutral"])

def get_enhanced_fallback(text, emotion):
    """Return enhanced fallback while model is loading"""
    # Parse text to make fallback more contextual
    text_lower = text.lower()
    
    if emotion == "sad":
        if any(w in text_lower for w in ["lost", "death", "died", "died"]):
            return "I'm so sorry for your loss. That must be incredibly painful. Would you like to share about what you've lost?"
        elif any(w in text_lower for w in ["alone", "lonely"]):
            return "Feeling alone is really hard. You're not the only one who feels this way. What's making you feel isolated right now?"
        else:
            return FALLBACK["sad"]
    
    elif emotion == "angry":
        if any(w in text_lower for w in ["someone", "friend", "family", "person"]):
            return "It sounds like someone has hurt you. That must feel betraying. Do you want to talk about what they did?"
        else:
            return FALLBACK["angry"]
    
    elif emotion == "anxious":
        if any(w in text_lower for w in ["work", "job", "deadline"]):
            return "Work stress is real. Many people feel this way. What specifically about this is worrying you the most?"
        elif any(w in text_lower for w in ["test", "exam", "failure"]):
            return "Exam anxiety is tough, but you're going to get through this. What's the biggest worry for you?"
        else:
            return FALLBACK["anxious"]
    
    elif emotion == "fear":
        if any(w in text_lower for w in ["dark", "alone", "outside"]):
            return "Specific fears like that are more common than you'd think. Can you tell me what specifically triggers this fear?"
        else:
            return FALLBACK["fear"]
    
    elif emotion == "happy":
        return FALLBACK["happy"]
    
    else:
        return FALLBACK["neutral"]