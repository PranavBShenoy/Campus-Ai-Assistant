from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.init_db import get_db
from app.database.models import User
from app.api.deps import get_current_user
from app.schemas.study_plan import GeneratePlanRequest, StudyPlanResponse, ModifyPlanRequest, ModifyPlanInstruction, UpdateSessionRequest
from app.services.study_plan_service import StudyPlanService
from typing import Optional

router = APIRouter()
plan_service = StudyPlanService()

@router.post("/generate", response_model=StudyPlanResponse)
async def generate_plan(
    request: GeneratePlanRequest, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return await plan_service.generate_plan(request, current_user.id, db)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@router.get("/", response_model=list[StudyPlanResponse])
async def list_plans(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await plan_service.get_plans(current_user.id, db)

@router.get("/{plan_id}", response_model=StudyPlanResponse)
async def get_plan(
    plan_id: str, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = await plan_service.get_plan(plan_id, current_user.id, db)
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found")
    return plan

@router.patch("/{plan_id}", response_model=StudyPlanResponse)
async def update_plan(
    plan_id: str, 
    updates: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = await plan_service.update_plan(plan_id, current_user.id, updates, db)
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found")
    return plan

@router.post("/{plan_id}/modify", response_model=StudyPlanResponse)
async def modify_plan(
    plan_id: str, 
    instruction: ModifyPlanInstruction, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    request = ModifyPlanRequest(plan_id=plan_id, instruction=instruction.instruction)
    try:
        plan = await plan_service.modify_plan(request, current_user.id, db)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found")
    return plan

@router.patch("/{plan_id}/sessions/{session_id}", response_model=StudyPlanResponse)
async def update_session(
    plan_id: str, 
    session_id: str, 
    request: UpdateSessionRequest, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    request.session_id = session_id
    try:
        plan = await plan_service.update_session(plan_id, current_user.id, request, db)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan or session not found")
    return plan
