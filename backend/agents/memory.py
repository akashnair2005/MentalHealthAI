import aiosqlite
import os
from datetime import datetime

# Simple SQLite initialization for Memory Agent
DB_PATH = "mindguardian_memory.db"

async def init_db():
    \"\"\"
    Initializes the database asynchronously.
    \"\"\"
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                timestamp TEXT,
                user_text TEXT,
                ai_response TEXT,
                detected_emotion TEXT,
                is_crisis BOOLEAN
            )
        ''')
        await db.commit()

async def store_interaction(user_id: str, text: str, response: str, emotion: str, is_crisis: bool):
    \"\"\"
    Stores the user interaction into the database asynchronously.
    \"\"\"
    timestamp = datetime.utcnow().isoformat()
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                INSERT INTO conversation_history (user_id, timestamp, user_text, ai_response, detected_emotion, is_crisis)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, timestamp, text, response, emotion, is_crisis))
            await db.commit()
    except Exception as e:
        print(f"Error saving to memory: {e}")

async def get_recent_history(user_id: str, limit: int = 10) -> list[dict]:
    \"\"\"
    Retrieves recent interactions for context asynchronously.
    \"\"\"
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT timestamp, user_text, ai_response, detected_emotion, is_crisis 
                FROM conversation_history 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
            
            history = []
            # We want them in chronological order for the prompt, but the query is DESC for limit
            for row in reversed(rows):
                history.append({
                    "timestamp": row["timestamp"],
                    "user_text": row["user_text"],
                    "ai_response": row["ai_response"],
                    "detected_emotion": row["detected_emotion"],
                    "is_crisis": bool(row["is_crisis"])
                })
            return history
    except Exception as e:
        print(f"Error reading from memory: {e}")
        return []

async def get_mood_history(user_id: str, limit: int = 50) -> list[dict]:
    \"\"\"
    Retrieves mood entries for the Analyzer asynchronously.
    \"\"\"
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT timestamp, detected_emotion 
                FROM conversation_history 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
            
            return [{"timestamp": row["timestamp"], "emotion": row["detected_emotion"]} for row in rows]
    except Exception as e:
        print(f"Error reading mood from memory: {e}")
        return []
