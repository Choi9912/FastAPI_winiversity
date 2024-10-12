from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base import Base
from datetime import datetime
from typing import List

# 채팅방 참가자를 위한 연결 테이블
chat_room_participants = Table(
    'chat_room_participants', 
    Base.metadata,
    Column('room_id', Integer, ForeignKey('chat_rooms.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)


class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    type: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))

    participants: Mapped[List["User"]] = relationship("User", secondary=chat_room_participants, back_populates="chat_rooms")
    messages: Mapped[List["ChatMessage"]] = relationship("ChatMessage", back_populates="room")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey('chat_rooms.id'))
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    content: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    room: Mapped["ChatRoom"] = relationship("ChatRoom", back_populates="messages")
    sender: Mapped["User"] = relationship("User", back_populates="sent_messages")