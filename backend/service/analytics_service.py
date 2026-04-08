from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.usage_event import UsageEvent
from backend.db.session import get_db

router = APIRouter(prefix="/costops/analytics", tags=["CostOps Analytics"])

@router.get("/models")
def model_costs(db: Session = Depends(get_db)):
    data = db.query(
        UsageEvent.model,
        func.sum(UsageEvent.cost)
    ).group_by(UsageEvent.model).all()

    return [{"model": m, "cost": c} for m, c in data]