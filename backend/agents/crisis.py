from backend.utils.llm_helper import generate_text_async

async def check_crisis(text: str) -> str:
    """
    Detects if the user is in a crisis situation (self-harm, suicide) asynchronously.
    Returns emergency response or "SAFE".
    """
    
    # Fast heuristic check for critical keywords
    critical_keywords = ["suicide", "kill myself", "end my life", "want to die", "self-harm", "cut myself", "no reason to live"]
    text_lower = text.lower()
    
    keyword_detected = any(keyword in text_lower for keyword in critical_keywords)
    
    prompt = f"""
    Detect if user is in crisis:
    - suicidal thoughts
    - self-harm intent
    - extreme hopelessness

    If detected:
    Return exactly this emergency response:
    "EMERGENCY: It sounds like you are going through a very difficult time. Please know you don't have to go through this alone. I strongly encourage you to contact a trusted person or call a helpline immediately. National Suicide Prevention Lifeline: 988"

    Else:
    Return "SAFE"

    User input: "{text}"
    """
    
    llm_response = await generate_text_async(prompt)
    
    # Fallback to keyword check if LLM mock is "SAFE" but keyword matched, or if API failed
    if keyword_detected and ("mock response" in llm_response.lower() or "SAFE" in llm_response):
        return "EMERGENCY: It sounds like you are going through a very difficult time. Please know you don't have to go through this alone. I strongly encourage you to contact a trusted person or call a helpline immediately. National Suicide Prevention Lifeline: 988"
        
    return llm_response
