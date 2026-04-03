from backend.utils.llm_helper import generate_text_async
from backend.agents.memory import get_recent_history

async def get_therapist_response(user_id: str, text: str, emotion: str) -> str:
    """
    Generates an empathetic response asynchronously, using recent conversation history for context.
    """
    
    # Fetch last 5 interactions for context
    history = await get_recent_history(user_id, limit=5)
    
    context_str = ""
    for entry in history:
        context_str += f"User: {entry['user_text']}\n"
        context_str += f"Assistant: {entry['ai_response']}\n"
        
    prompt = f"""
    Act as a compassionate, professional therapist in a follow-up conversation.
    
    Guidelines:
    - Be empathetic and warm.
    - Do NOT give medical advice or diagnoses.
    - Encourage the user to express their feelings further.
    - Use insights from the conversation history if relevant to show you are listening.
    - Ask a reflective question at the end.

    Conversation History:
    {context_str}

    Current User Status:
    Detected Emotion: {emotion}
    User Message: {text}

    Response:
    """
    
    return await generate_text_async(prompt)
