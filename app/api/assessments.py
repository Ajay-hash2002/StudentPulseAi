import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Student, Assessment, Skill, StudentSkillEvidence
from app.schemas.assessment import AssessmentCreate, AssessmentResponse
from app.schemas.envelope import ApiResponse
from app.api.deps import get_current_student
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/assessments", tags=["Assessments"])

@router.get("", response_model=ApiResponse)
def list_assessments(
    request: Request,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    assessments = (
        db.query(Assessment)
        .filter(Assessment.student_id == current_student.student_id)
        .order_by(Assessment.completed_at.desc())
        .all()
    )
    result = [
        {
            "assessment_id": a.assessment_id,
            "assessment_type": a.assessment_type,
            "score_or_result": a.score_or_result,
            "max_score": a.max_score,
            "completed_at": a.completed_at.isoformat()
        } for a in assessments
    ]
    return ApiResponse(success=True, data=result, request_id=req_id)

@router.post("", response_model=ApiResponse)
def submit_assessment(
    req: AssessmentCreate,
    request: Request,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    now = datetime.now(timezone.utc)
    assessment = Assessment(
        student_id=current_student.student_id,
        assessment_type=req.assessment_type.strip(),
        score_or_result=req.score_or_result,
        max_score=req.max_score,
        completed_at=now
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    # Correlate assessment with skills (e.g. Python Quiz -> Python skill evidence)
    type_lower = req.assessment_type.lower()
    skill_match = None
    if "python" in type_lower:
        skill_match = "Python"
    elif "dsa" in type_lower or "data structure" in type_lower:
        skill_match = "Data Structures"
    elif "algorithm" in type_lower:
        skill_match = "Algorithms"
    elif "sql" in type_lower or "database" in type_lower:
        skill_match = "SQL"
    elif "comm" in type_lower:
        skill_match = "Communication"

    if skill_match:
        skill = db.query(Skill).filter(Skill.skill_name == skill_match).first()
        if skill:
            pct = (req.score_or_result / req.max_score) * 100
            if pct >= 85:
                lvl = 3
            elif pct >= 65:
                lvl = 2
            else:
                lvl = 1
            ev = StudentSkillEvidence(
                student_id=current_student.student_id,
                skill_id=skill.skill_id,
                source_type="assessment",
                evidence_reference=f"Assessment: {req.assessment_type} ({req.score_or_result}/{req.max_score})",
                observed_level=lvl,
                date=now
            )
            db.add(ev)
            db.commit()

    log_audit_event(db, actor_id=current_student.student_id, action_type="SUBMIT_ASSESSMENT", outcome="SUCCESS")
    data = {
        "assessment_id": assessment.assessment_id,
        "assessment_type": assessment.assessment_type,
        "score_or_result": assessment.score_or_result,
        "max_score": assessment.max_score,
        "completed_at": assessment.completed_at.isoformat()
    }
    return ApiResponse(success=True, data=data, request_id=req_id)
