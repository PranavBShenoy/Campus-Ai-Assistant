from app.api.deps import get_current_user
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.init_db import get_db
from app.database.models import User
from app.schemas.evaluation import RunEvaluationRequest, EvaluationRunResponse
from app.services.evaluation_service import EvaluationService

router = APIRouter()
eval_service = EvaluationService()

@router.post("/run", response_model=EvaluationRunResponse)
async def run_evaluation(
    request: RunEvaluationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await eval_service.run_evaluation(request, current_user.id, db)
