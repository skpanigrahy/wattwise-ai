from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.models.usage_event import UsageEvent
from backend.service.cost_calculator import calculate_cost
from backend.db.session import get_db

router = APIRouter(prefix="/costops", tags=["CostOps"])

@router.post("/usage")
def create_usage_event(payload: dict, db: Session = Depends(get_db)):
    cost = calculate_cost(
        payload["model"],
        payload["input_tokens"],
        payload["output_tokens"]
    )

    event = UsageEvent(
        user_id=payload["user_id"],
        model=payload["model"],
        source=payload["source"],
        input_tokens=payload["input_tokens"],
        output_tokens=payload["output_tokens"],
        cost=cost
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return {"cost": cost}