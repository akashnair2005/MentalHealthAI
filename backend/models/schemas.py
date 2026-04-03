from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    text: str
    user_id: str = "default_user"

class ChatResponse(BaseModel):
    response: str
    emotion: str
    is_crisis: bool
    suggestions: List[str]

class MoodEntry(BaseModel):
    emotion: str
    timestamp: str

class MoodHistoryResponse(BaseModel):
    history: List[MoodEntry]
    trend_analysis: str
