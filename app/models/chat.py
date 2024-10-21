from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base import Base
from datetime import datetime
from typing import List


# 중간 테이블 정의
chat_room_participants = Table('chat_room_participants', Base.metadata,
    Column('room_id', Integer, ForeignKey('chat_rooms.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)  # "admin_student", "student_student", "group"
    creator_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="created_rooms")
    messages = relationship("ChatMessage", back_populates="room")
    participants = relationship("User", secondary=chat_room_participants, back_populates="chat_rooms")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)

    room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User", back_populates="messages")
