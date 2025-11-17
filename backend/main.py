from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from database import create_document, get_documents
from schemas import Conversation, Message, Preset

app = FastAPI(title="Creative Chat LLM API", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    preset_id: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    timestamp: datetime


@app.get("/test")
async def test_db():
    try:
        items = await get_documents("conversation", {}, limit=1)
        return {"ok": True, "connected": True, "sample": items}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/conversations", response_model=Dict[str, Any])
async def create_conversation(conv: Conversation):
    created = await create_document("conversation", conv.model_dump())
    if not created:
        raise HTTPException(status_code=500, detail="Failed to create conversation")
    return created


@app.get("/conversations", response_model=List[Dict[str, Any]])
async def list_conversations(limit: int = 50):
    return await get_documents("conversation", {}, limit=limit)


@app.post("/messages", response_model=Dict[str, Any])
async def create_message(msg: Message):
    created = await create_document("message", msg.model_dump())
    if not created:
        raise HTTPException(status_code=500, detail="Failed to create message")
    return created


@app.get("/messages", response_model=List[Dict[str, Any]])
async def list_messages(conversation_id: Optional[str] = None, limit: int = 100):
    filt = {"conversation_id": conversation_id} if conversation_id else {}
    return await get_documents("message", filt, limit=limit)


# Simple mock chat generation to keep UX working without external providers
# In real app, you'd integrate OpenAI/Anthropic here.
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    # Create conversation if not provided
    conv_id = req.conversation_id or (await create_document("conversation", {"title": "New Chat"}))['id']

    # Store user message
    await create_document("message", {
        "conversation_id": conv_id,
        "role": "user",
        "content": req.message,
        "model": None,
        "tokens": None,
    })

    # Generate a playful, creative assistant reply (mock)
    reply = (
        "Let's make something beautiful. "
        "Here's a spark: imagine your idea as light through a lens—what do you want it to reveal?"
    )

    # Store assistant message
    created = await create_document("message", {
        "conversation_id": conv_id,
        "role": "assistant",
        "content": reply,
        "model": "mock-model",
        "tokens": 24,
    })

    return ChatResponse(conversation_id=conv_id, reply=created.get("content", reply), timestamp=datetime.utcnow())


@app.get("/presets", response_model=List[Dict[str, Any]])
async def list_presets(limit: int = 50):
    # Provide a few built-in creative presets
    builtins = [
        {"name": "Cinematic Muse", "system_prompt": "You are a film director guiding mood and pacing.", "temperature": 0.8, "creativity": 90},
        {"name": "Photo Stylist", "system_prompt": "You are a photography art director.", "temperature": 0.7, "creativity": 70},
        {"name": "Minimal Poet", "system_prompt": "You respond with minimal, evocative language.", "temperature": 0.6, "creativity": 60},
    ]
    return builtins[:limit]
