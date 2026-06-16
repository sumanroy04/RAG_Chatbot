from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from backend.app.extensions import get_db
from backend.api.models.crisis import CrisisLog
from backend.auth.routes import get_current_user
from backend.auth.models import User

crisis_router = APIRouter()

class CrisisLogSchema(BaseModel):
    id: int
    user_id: int | None
    message: str
    matched_keywords: str
    created_at: datetime

    class Config:
        from_attributes = True

@crisis_router.get("/logs", response_model=List[CrisisLogSchema])
def get_crisis_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Admins or therapists see all crisis logs for intervention; regular users only see their own logs
    if current_user.role in ["admin", "therapist"]:
        return db.query(CrisisLog).order_by(CrisisLog.created_at.desc()).all()
    else:
        return db.query(CrisisLog).filter(CrisisLog.user_id == current_user.id).order_by(CrisisLog.created_at.desc()).all()
