from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from backend.models.schemas import ChatMessage, ChatResponse, MoodHistoryResponse
from backend.agents.listener import detect_emotion
from backend.agents.crisis import check_crisis
from backend.agents.therapist import get_therapist_response
from backend.agents.action import get_action_suggestions
from backend.agents.memory import store_interaction, get_mood_history, init_db
from backend.agents.analyzer import analyze_mood_trends

app = FastAPI(title="MindGuardian AI", description="Multi-agent mental health system")

# CORS middleware to allow arbitrary origins for local HTML/JS dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the frontend directory to serve index.html and static assets
# This ensures the UI and API are on the same origin, avoiding CORS/file-protocol issues.
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

@app.on_event("startup")
async def startup_event():
    # Properly initialize the async DB
    await init_db()

@app.post("/api/chat", response_model=ChatResponse)
async def chat_interaction(message: ChatMessage):
    try:
        user_text = message.text
        user_id = message.user_id

        # Agent 3: Crisis Agent check First
        crisis_result = await check_crisis(user_text)
        is_crisis = "EMERGENCY:" in crisis_result.upper()

        if is_crisis:
            response_text = crisis_result
            emotion = "Crisis"
            suggestions = ["Please reach out to an emergency contact or lifeline immediately."]
            
            # Agent 5: Store Memory
            await store_interaction(user_id, user_text, response_text, emotion, is_crisis)
            
            return ChatResponse(
                response=response_text,
                emotion=emotion,
                is_crisis=True,
                suggestions=suggestions
            )

        # Agent 1: Listener Agent detects emotion
        emotion = await detect_emotion(user_text)

        # Agent 2: Therapist Agent generates empathetic response (Now Context-Aware)
        response_text = await get_therapist_response(user_id, user_text, emotion)

        # Agent 4: Action Agent gets suggestions based on emotion
        suggestions = get_action_suggestions(emotion)

        # Agent 5: Store Memory
        await store_interaction(user_id, user_text, response_text, emotion, is_crisis=False)

        return ChatResponse(
            response=response_text,
            emotion=emotion,
            is_crisis=False,
            suggestions=suggestions
        )
        
    except Exception as e:
        print(f"Error handling chat: {e}")
        # Log detail for easier debugging but return generic message
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mood_history", response_model=MoodHistoryResponse)
async def get_history(user_id: str = "default_user"):
    try:
        # Get raw entries
        history = await get_mood_history(user_id, limit=20)
        
        # Agent 6: Analyzer details
        trend = await analyze_mood_trends(user_id)
        
        return MoodHistoryResponse(
            history=history,
            trend_analysis=trend
        )
    except Exception as e:
        print(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail="Error fetching history.")
