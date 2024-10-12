from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class ChatRoomBase(BaseModel):
    name: str
    type: str


class ChatRoomCreate(ChatRoomBase):
    pass


class ChatRoom(ChatRoomBase):
    id: int
    created_at: datetime
    created_by: int

    model_config = ConfigDict(from_attributes=True)


class ChatMessageBase(BaseModel):
    content: str


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessage(ChatMessageBase):
    id: int
    room_id: int
    sender_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatRoomWithMessages(ChatRoom):
    messages: List[ChatMessage] = []


class ChatRoomInvite(BaseModel):
    user_id: int