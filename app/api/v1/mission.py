from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...schemas import mission as mission_schema
from ...models.user import User
from ...db.session import get_async_db
from ...api.dependencies import get_current_active_user
from ...services.mission_service import MissionService

router = APIRouter(prefix="/missions", tags=["missions"])

@router.get("/", response_model=List[mission_schema.MissionInDB])
async def get_missions(
    db: AsyncSession = Depends(get_async_db),
    mission_service: MissionService = Depends()
):
    missions = await mission_service.get_missions(db)
    return [mission_schema.MissionInDB.from_orm(mission) for mission in missions]

@router.get("/{mission_id}", response_model=mission_schema.MissionInDB)
async def retrieve_mission(
    mission_id: int,
    db: AsyncSession = Depends(get_async_db),
    mission_service: MissionService = Depends()
):
    mission = await mission_service.retrieve_mission(db, mission_id)
    return mission_schema.MissionInDB.from_orm(mission)

@router.post("/{mission_id}/submit", response_model=mission_schema.MissionSubmissionInDB)
async def submit_mission(
    mission_id: int,
    submission: mission_schema.MissionSubmissionCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    mission_service: MissionService = Depends()
):
    return await mission_service.submit_mission(db, mission_id, current_user.id, submission)

@router.post("/", response_model=mission_schema.MissionInDB)
async def create_mission(
    mission: mission_schema.MissionCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    mission_service: MissionService = Depends()
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only administrators can create missions")
    return await mission_service.create_mission(db, mission)