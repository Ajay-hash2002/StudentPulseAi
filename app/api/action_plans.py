import json
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Student, CareerGoal, ActionPlanItem
from app.schemas.action_plan import (
    ActionPlanCreateRequest, ActionPlanResponse, ActionPlanItemResponse, ActionStatusUpdate
)
from app.schemas.envelope import ApiResponse, ErrorDetail
from app.api.deps import get_current_student
from app.analysis.profile_features import extract_profile_features
from app.analysis.skill_gap import analyze_skill_gaps
from app.analysis.readiness import calculate_readiness_score
from app.analysis.recommendations import generate_recommendations
from app.ai.ai_explainer import explain_readiness_and_gaps
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/action-plans", tags=["Action Plans"])

@router.post("", response_model=ApiResponse)
def generate_action_plan(
    req: ActionPlanCreateRequest,
    request: Request,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    # 1. Resolve role
    target_role = req.target_role
    goal_id = req.goal_id
    if not target_role:
        if goal_id:
            goal = db.query(CareerGoal).filter(
                CareerGoal.goal_id == goal_id,
                CareerGoal.student_id == current_student.student_id
            ).first()
            if goal:
                target_role = goal.target_role
        if not target_role:
            latest_goal = (
                db.query(CareerGoal)
                .filter(CareerGoal.student_id == current_student.student_id)
                .order_by(CareerGoal.created_at.desc())
                .first()
            )
            target_role = latest_goal.target_role if latest_goal else "Backend Developer"

    # 2. Extract profile and run intelligence calculations
    features = extract_profile_features(db, current_student.student_id)
    gap_analysis = analyze_skill_gaps(features, target_role)
    readiness_data = calculate_readiness_score(features, target_role)
    candidate_actions = generate_recommendations(gap_analysis)

    # 3. Explain via AI layer / deterministic fallback
    explanation = explain_readiness_and_gaps(gap_analysis, readiness_data, candidate_actions)

    # 4. Save action items in DB for tracking
    plan_id = f"plan_{current_student.student_id}"
    
    # Clean previous todo items for this student to avoid runaway duplication
    db.query(ActionPlanItem).filter(
        ActionPlanItem.student_id == current_student.student_id,
        ActionPlanItem.status == "todo"
    ).delete()

    created_items = []
    now = datetime.now(timezone.utc)
    for act in candidate_actions[:6]:
        item = ActionPlanItem(
            student_id=current_student.student_id,
            goal_id=goal_id or plan_id,
            action_text=act["action_text"],
            reason=act["reason"],
            evidence_refs=json.dumps(act.get("evidence_refs", [])),
            priority=act["priority"],
            status="todo",
            created_at=now
        )
        db.add(item)
        db.flush()
        created_items.append(item)
    db.commit()

    log_audit_event(db, actor_id=current_student.student_id, action_type="GENERATE_ACTION_PLAN", outcome="SUCCESS")

    # Fetch all items for this student to compute progress
    all_items = db.query(ActionPlanItem).filter(ActionPlanItem.student_id == current_student.student_id).all()
    done_count = len([i for i in all_items if i.status == "done"])
    progress = round((done_count / len(all_items) * 100.0), 1) if all_items else 0.0

    items_res = []
    for item in all_items:
        try:
            refs = json.loads(item.evidence_refs)
        except Exception:
            refs = []
        items_res.append({
            "recommendation_id": item.recommendation_id,
            "action_text": item.action_text,
            "reason": item.reason,
            "evidence_refs": refs,
            "priority": item.priority,
            "status": item.status,
            "created_at": item.created_at.isoformat()
        })

    response_data = {
        "plan_id": plan_id,
        "target_role": target_role,
        "summary_explanation": explanation.get("summary", ""),
        "explanation_source": explanation.get("source", "Deterministic Rule-based Explainer"),
        "actions": items_res,
        "progress_pct": progress,
        "limitations": explanation.get("limitations", [])
    }
    return ApiResponse(success=True, data=response_data, request_id=req_id)

@router.get("/{plan_id}", response_model=ApiResponse)
def get_action_plan(
    plan_id: str,
    request: Request,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # Access control verification: students can only access their own action plan
    if plan_id.startswith("plan_"):
        owner_id = plan_id[len("plan_"):]
        if owner_id and owner_id != current_student.student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you do not have permission to view another student's action plan."
            )

    items = (
        db.query(ActionPlanItem)
        .filter(ActionPlanItem.student_id == current_student.student_id)
        .order_by(ActionPlanItem.created_at.desc())
        .all()
    )
    done_count = len([i for i in items if i.status == "done"])
    progress = round((done_count / len(items) * 100.0), 1) if items else 0.0

    items_res = []
    for item in items:
        try:
            refs = json.loads(item.evidence_refs)
        except Exception:
            refs = []
        items_res.append({
            "recommendation_id": item.recommendation_id,
            "action_text": item.action_text,
            "reason": item.reason,
            "evidence_refs": refs,
            "priority": item.priority,
            "status": item.status,
            "created_at": item.created_at.isoformat()
        })

    data = {
        "plan_id": plan_id,
        "target_role": "Personalized Career Plan",
        "summary_explanation": "Prioritized action items mapped to your identified skill gaps.",
        "explanation_source": "Deterministic Rule-based Explainer",
        "actions": items_res,
        "progress_pct": progress,
        "limitations": [
            "Actions are generated based on currently recorded evidence.",
            "Items can be updated dynamically as you complete practice steps."
        ]
    }
    return ApiResponse(success=True, data=data, request_id=req_id)

@router.patch("/{plan_id}/items/{item_id}", response_model=ApiResponse)
def update_action_item_status(
    plan_id: str,
    item_id: str,
    req: ActionStatusUpdate,
    request: Request,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    item = db.query(ActionPlanItem).filter(
        ActionPlanItem.recommendation_id == item_id,
        ActionPlanItem.student_id == current_student.student_id
    ).first()

    if not item:
        # Check if item exists for another student -> 403 Forbidden
        other_item = db.query(ActionPlanItem).filter(ActionPlanItem.recommendation_id == item_id).first()
        if other_item:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you cannot modify another student's action item."
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action item not found."
        )

    item.status = req.status
    db.commit()
    db.refresh(item)

    log_audit_event(
        db,
        actor_id=current_student.student_id,
        action_type="UPDATE_ACTION_STATUS",
        outcome=f"UPDATED_TO_{req.status.upper()}"
    )

    try:
        refs = json.loads(item.evidence_refs)
    except Exception:
        refs = []

    data = {
        "recommendation_id": item.recommendation_id,
        "action_text": item.action_text,
        "reason": item.reason,
        "evidence_refs": refs,
        "priority": item.priority,
        "status": item.status,
        "created_at": item.created_at.isoformat()
    }
    return ApiResponse(success=True, data=data, request_id=req_id)
