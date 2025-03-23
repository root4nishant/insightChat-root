from pydantic import BaseModel
from typing import List

class ChatPayload(BaseModel):
    messages: List[str]

class ChatRecord(BaseModel):
    user_id: str
    messages: List[str]
    analysis: str
