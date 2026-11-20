import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Student, CareerGoal
from app.schemas.student import CareerGoalCreate, CareerGoalResponse
from app.schemas.envelope import ApiResponse
from app.api.deps import get_current_student
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/career-goals", tags=["Career Goals"])

@router.get("", response_model=ApiResponse)
def get_career_goals(
    request: Request,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    goals = (
        db.query(CareerGoal)
        .filter(CareerGoal.student_id == current_student.student_id)
        .order_by(CareerGoal.created_at.desc())
        .all()
    )
    result = [
        {
            "goal_id": g.goal_id,
            "target_role": g.target_role,
            "target_date": g.target_date,
            "notes": g.notes,
            "created_at": g.created_at.isoformat()
        } for g in goals
    ]
    return ApiResponse(success=True, data=result, request_id=req_id)

@router.post("", response_model=ApiResponse)
def create_career_goal(
    req: CareerGoalCreate,
    request: Request,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    goal = CareerGoal(
        student_id=current_student.student_id,
        target_role=req.target_role.strip(),
        target_date=req.target_date,
        notes=req.notes,
        created_at=datetime.now(timezone.utc)
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)

    log_audit_event(db, actor_id=current_student.student_id, action_type="SET_CAREER_GOAL", outcome="SUCCESS")
    data = {
        "goal_id": goal.goal_id,
        "target_role": goal.target_role,
        "target_date": goal.target_date,
        "notes": goal.notes,
        "created_at": goal.created_at.isoformat()
    }
    return ApiResponse(success=True, data=data, request_id=req_id)
