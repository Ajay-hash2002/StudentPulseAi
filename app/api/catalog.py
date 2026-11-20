import uuid
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Skill
from app.schemas.envelope import ApiResponse
from app.analysis.skill_gap import load_role_requirements

router = APIRouter(prefix="/catalog", tags=["Catalog"])

@router.get("/roles", response_model=ApiResponse)
def get_roles_catalog(request: Request):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    roles_data = load_role_requirements()
    return ApiResponse(success=True, data=roles_data.get("roles", []), request_id=req_id)

@router.get("/skills", response_model=ApiResponse)
def get_skills_catalog(request: Request, db: Session = Depends(get_db)):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    skills = db.query(Skill).all()
    result = [
        {
            "skill_id": s.skill_id,
            "skill_name": s.skill_name,
            "description": s.description,
            "category": s.category
        } for s in skills
    ]
    return ApiResponse(success=True, data=result, request_id=req_id)
