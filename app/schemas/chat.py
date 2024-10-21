from pydantic import BaseModel
from datetime import datetime
from typing import List

class ChatRoomBase(BaseModel):
    name: str
    type: str

class ChatRoomCreate(ChatRoomBase):
    pass

class ChatRoom(ChatRoomBase):
    id: int
    creator_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class ChatMessageBase(BaseModel):
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessage(ChatMessageBase):
    id: int
    room_id: int
    sender_id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class ChatRoomParticipant(BaseModel):
    room_id: int
    user_id: int

    class Config:
        orm_mode = True