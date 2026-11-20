from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Student, CareerGoal
from app.schemas.analysis import (
    SkillGapRequest, SkillGapResponse, ReadinessResponse,
    ProjectReadinessResponse, InterviewReadinessResponse
)
from app.schemas.envelope import ApiResponse, ErrorDetail
from app.api.deps import get_current_student
from app.analysis.profile_features import extract_profile_features
from app.analysis.skill_gap import analyze_skill_gaps
from app.analysis.readiness import calculate_readiness_score
from app.analysis.project_readiness import analyze_project_readiness
from app.analysis.interview_readiness import analyze_interview_readiness

router = APIRouter(prefix="/analysis", tags=["Analysis"])

def resolve_target_role(req: SkillGapRequest, current_student: Student, db: Session) -> str:
    if req.target_role and req.target_role.strip():
        return req.target_role.strip()
    if req.goal_id:
        goal = db.query(CareerGoal).filter(
            CareerGoal.goal_id == req.goal_id,
            CareerGoal.student_id == current_student.student_id
        ).first()
        if goal:
            return goal.target_role
    # Fallback to latest goal
    latest_goal = (
        db.query(CareerGoal)
        .filter(CareerGoal.student_id == current_student.student_id)
        .order_by(CareerGoal.created_at.desc())
        .first()
    )
    if latest_goal:
        return latest_goal.target_role
    return "Backend Developer"  # Default baseline

@router.post("/skill-gaps", response_model=ApiResponse)
def get_skill_gaps(
    req: SkillGapRequest,
    request: Request,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    target_role = resolve_target_role(req, current_student, db)
    features = extract_profile_features(db, current_student.student_id)
    analysis = analyze_skill_gaps(features, target_role)
    analysis["generated_at"] = datetime.now(timezone.utc).isoformat()
    return ApiResponse(success=True, data=analysis, request_id=req_id)

@router.post("/readiness", response_model=ApiResponse)
def get_readiness_score(
    req: SkillGapRequest,
    request: Request,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    target_role = resolve_target_role(req, current_student, db)
    features = extract_profile_features(db, current_student.student_id)
    readiness = calculate_readiness_score(features, target_role)
    readiness["generated_at"] = datetime.now(timezone.utc).isoformat()
    return ApiResponse(success=True, data=readiness, request_id=req_id)

@router.post("/project-readiness", response_model=ApiResponse)
def get_project_readiness(
    req: SkillGapRequest,
    request: Request,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    target_role = resolve_target_role(req, current_student, db)
    features = extract_profile_features(db, current_student.student_id)
    result = analyze_project_readiness(features, target_role)
    return ApiResponse(success=True, data=result, request_id=req_id)

@router.post("/interview-readiness", response_model=ApiResponse)
def get_interview_readiness(
    request: Request,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    features = extract_profile_features(db, current_student.student_id)
    result = analyze_interview_readiness(features)
    return ApiResponse(success=True, data=result, request_id=req_id)
