from pydantic import BaseModel, Field
from typing import Optional, List

# Each Pydantic model corresponds to a MongoDB collection (lowercased class name)

class Conversation(BaseModel):
    user_id: Optional[str] = Field(None, description="Owner of the conversation")
    title: str = Field(..., min_length=1, max_length=120)

class Message(BaseModel):
    conversation_id: str = Field(..., description="Related conversation id")
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)
    model: Optional[str] = Field(None, description="Model used for assistant messages")
    tokens: Optional[int] = Field(None, ge=0)

class Preset(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    system_prompt: Optional[str] = None
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    creativity: Optional[int] = Field(None, ge=0, le=100)

