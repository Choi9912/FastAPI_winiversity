from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...schemas import chat as chat_schema
from ...models.user import User, UserRole
from ...models.chat import ChatRoom, ChatMessage
from ...db.session import get_async_db
from ...api.dependencies import get_current_active_user
from sqlalchemy import select, and_
import json

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    dependencies=[Depends(get_current_active_user)],
)

# 연결된 클라이언트를 저장할 딕셔너리
connected_clients = {}

@router.post("/rooms", response_model=chat_schema.ChatRoom)
async def create_chat_room(
    room: chat_schema.ChatRoomCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    새로운 채팅방을 생성합니다.
    - 관리자는 학생과의 1:1 채팅방 생성 가능
    - 학생은 다른 학생과의 채팅방 생성 가능
    """
    if current_user.role == UserRole.ADMIN and room.type != "admin_student":
        raise HTTPException(status_code=400, detail="관리자는 학생과의 1:1 채팅만 생성할 수 있습니다.")
    
    if current_user.role == UserRole.STUDENT and room.type not in ["student_student", "group"]:
        raise HTTPException(status_code=400, detail="학생은 다른 학생과의 1:1 또는 그룹 채팅만 생성할 수 있습니다.")
    
    new_room = ChatRoom(
        name=room.name,
        type=room.type,
        created_by=current_user.id
    )
    db.add(new_room)
    await db.commit()
    await db.refresh(new_room)
    return new_room

@router.get("/rooms", response_model=List[chat_schema.ChatRoom])
async def get_chat_rooms(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    현재 사용자가 참여 중인 모든 채팅방을 조회합니다.
    """
    query = select(ChatRoom).where(ChatRoom.participants.any(id=current_user.id))
    result = await db.execute(query)
    rooms = result.scalars().all()
    return rooms

@router.post("/rooms/{room_id}/messages", response_model=chat_schema.ChatMessage)
async def send_message(
    room_id: int,
    message: chat_schema.ChatMessageCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    특정 채팅방에 메시지를 전송합니다.
    """
    room = await db.get(ChatRoom, room_id)
    if not room or current_user.id not in [p.id for p in room.participants]:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없거나 접근 권한이 없습니다.")
    
    new_message = ChatMessage(
        room_id=room_id,
        sender_id=current_user.id,
        content=message.content
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message

@router.get("/rooms/{room_id}/messages", response_model=List[chat_schema.ChatMessage])
async def get_messages(
    room_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    특정 채팅방의 모든 메시지를 조회합니다.
    """
    room = await db.get(ChatRoom, room_id)
    if not room or current_user.id not in [p.id for p in room.participants]:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없거나 접근 권한이 없습니다.")
    
    query = select(ChatMessage).where(ChatMessage.room_id == room_id).order_by(ChatMessage.timestamp)
    result = await db.execute(query)
    messages = result.scalars().all()
    return messages

@router.post("/rooms/{room_id}/invite", status_code=status.HTTP_204_NO_CONTENT)
async def invite_to_chat_room(
    room_id: int,
    invite: chat_schema.ChatRoomInvite,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    다른 사용자를 채팅방에 초대합니다.
    """
    room = await db.get(ChatRoom, room_id)
    if not room or current_user.id not in [p.id for p in room.participants]:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없거나 접근 권한이 없습니다.")
    
    invited_user = await db.get(User, invite.user_id)
    if not invited_user:
        raise HTTPException(status_code=404, detail="초대할 사용자를 찾을 수 없습니다.")
    
    if invited_user in room.participants:
        raise HTTPException(status_code=400, detail="이미 채팅방에 참여 중인 사용자입니다.")
    
    room.participants.append(invited_user)
    await db.commit()

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    await websocket.accept()
    
    if room_id not in connected_clients:
        connected_clients[room_id] = []
    connected_clients[room_id].append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # 메시지를 데이터베이스에 저장
            new_message = ChatMessage(
                room_id=room_id,
                sender_id=current_user.id,
                content=message_data['content']
            )
            db.add(new_message)
            await db.commit()
            
            # 같은 방에 있는 모든 클라이언트에게 메시지 전송
            for client in connected_clients[room_id]:
                await client.send_text(json.dumps({
                    "sender": current_user.username,
                    "content": message_data['content']
                }))
    except WebSocketDisconnect:
        connected_clients[room_id].remove(websocket)
