import json
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Student, Skill, StudentSkillEvidence, Project, Certification
from app.schemas.auth import StudentProfile
from app.schemas.student import (
    StudentUpdate, EvidenceCreate, EvidenceResponse,
    ProjectCreate, ProjectResponse, CertificationCreate, CertificationResponse
)
from app.schemas.envelope import ApiResponse, ErrorDetail
from app.api.deps import get_current_student
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/me", response_model=ApiResponse)
def get_own_profile(request: Request, current_student: Student = Depends(get_current_student)):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    profile = StudentProfile.model_validate(current_student)
    return ApiResponse(success=True, data=profile.model_dump(), request_id=req_id)

@router.patch("/me", response_model=ApiResponse)
def update_own_profile(
    req: StudentUpdate,
    request: Request,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    if req.display_name:
        current_student.display_name = req.display_name.strip()
        db.commit()
        db.refresh(current_student)
    profile = StudentProfile.model_validate(current_student)
    return ApiResponse(success=True, data=profile.model_dump(), request_id=req_id)

@router.get("/me/evidence", response_model=ApiResponse)
def get_own_evidence(
    request: Request,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    records = (
        db.query(StudentSkillEvidence, Skill.skill_name)
        .join(Skill, StudentSkillEvidence.skill_id == Skill.skill_id)
        .filter(StudentSkillEvidence.student_id == current_student.student_id)
        .order_by(StudentSkillEvidence.date.desc())
        .all()
    )
    result = [
        {
            "evidence_id": ev.evidence_id,
            "skill_id": ev.skill_id,
            "skill_name": sname,
            "source_type": ev.source_type,
            "evidence_reference": ev.evidence_reference,
            "observed_level": ev.observed_level,
            "date": ev.date.isoformat()
        } for ev, sname in records
    ]
    return ApiResponse(success=True, data=result, request_id=req_id)

@router.post("/me/skills", response_model=ApiResponse)
def add_skill_evidence(
    req: EvidenceCreate,
    request: Request,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    skill = db.query(Skill).filter(Skill.skill_name.ilike(req.skill_name.strip())).first()
    if not skill:
        # Create custom skill dynamically if not found in catalog
        skill_id = f"skill_{req.skill_name.lower().replace(' ', '_')}"
        skill = Skill(
            skill_id=skill_id,
            skill_name=req.skill_name.strip(),
            description=f"User added skill {req.skill_name}",
            category="Technical"
        )
        db.add(skill)
        db.commit()
        db.refresh(skill)

    evidence = StudentSkillEvidence(
        student_id=current_student.student_id,
        skill_id=skill.skill_id,
        source_type=req.source_type,
        evidence_reference=req.evidence_reference.strip(),
        observed_level=req.observed_level,
        date=datetime.now(timezone.utc)
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    log_audit_event(db, actor_id=current_student.student_id, action_type="ADD_EVIDENCE", outcome="SUCCESS")
    data = {
        "evidence_id": evidence.evidence_id,
        "skill_id": skill.skill_id,
        "skill_name": skill.skill_name,
        "source_type": evidence.source_type,
        "evidence_reference": evidence.evidence_reference,
        "observed_level": evidence.observed_level,
        "date": evidence.date.isoformat()
    }
    return ApiResponse(success=True, data=data, request_id=req_id)

@router.get("/me/projects", response_model=ApiResponse)
def list_own_projects(
    request: Request,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    projects = db.query(Project).filter(Project.student_id == current_student.student_id).all()
    result = []
    for p in projects:
        try:
            skills = json.loads(p.skills_used)
        except Exception:
            skills = []
        result.append({
            "project_id": p.project_id,
            "title": p.title,
            "description": p.description,
            "skills_used": skills,
            "status": p.status,
            "created_at": p.created_at.isoformat()
        })
    return ApiResponse(success=True, data=result, request_id=req_id)

@router.post("/me/projects", response_model=ApiResponse)
def add_project(
    req: ProjectCreate,
    request: Request,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    project = Project(
        student_id=current_student.student_id,
        title=req.title.strip(),
        description=req.description.strip(),
        skills_used=json.dumps(req.skills_used),
        status=req.status,
        created_at=datetime.now(timezone.utc)
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Automatically log evidence for the skills used in this project
    for sname in req.skills_used:
        skill = db.query(Skill).filter(Skill.skill_name.ilike(sname.strip())).first()
        if skill:
            ev = StudentSkillEvidence(
                student_id=current_student.student_id,
                skill_id=skill.skill_id,
                source_type="project",
                evidence_reference=f"Project: {project.title}",
                observed_level=2 if project.status != "completed" else 3,
                date=datetime.now(timezone.utc)
            )
            db.add(ev)
    db.commit()

    log_audit_event(db, actor_id=current_student.student_id, action_type="ADD_PROJECT", outcome="SUCCESS")
    data = {
        "project_id": project.project_id,
        "title": project.title,
        "description": project.description,
        "skills_used": req.skills_used,
        "status": project.status,
        "created_at": project.created_at.isoformat()
    }
    return ApiResponse(success=True, data=data, request_id=req_id)

@router.get("/me/certifications", response_model=ApiResponse)
def list_own_certifications(
    request: Request,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    certs = db.query(Certification).filter(Certification.student_id == current_student.student_id).all()
    result = [
        {
            "certification_id": c.certification_id,
            "name": c.name,
            "issuer": c.issuer,
            "issue_date": c.issue_date.isoformat(),
            "verification_reference": c.verification_reference
        } for c in certs
    ]
    return ApiResponse(success=True, data=result, request_id=req_id)

@router.post("/me/certifications", response_model=ApiResponse)
def add_certification(
    req: CertificationCreate,
    request: Request,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    cert = Certification(
        student_id=current_student.student_id,
        name=req.name.strip(),
        issuer=req.issuer.strip(),
        issue_date=datetime.now(timezone.utc),
        verification_reference=req.verification_reference
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)

    log_audit_event(db, actor_id=current_student.student_id, action_type="ADD_CERTIFICATION", outcome="SUCCESS")
    data = {
        "certification_id": cert.certification_id,
        "name": cert.name,
        "issuer": cert.issuer,
        "issue_date": cert.issue_date.isoformat(),
        "verification_reference": cert.verification_reference
    }
    return ApiResponse(success=True, data=data, request_id=req_id)

@router.delete("/me", response_model=ApiResponse)
def delete_own_account(
    request: Request,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    actor_id = current_student.student_id
    db.delete(current_student)
    db.commit()
    log_audit_event(db, actor_id=actor_id, action_type="DELETE_ACCOUNT", outcome="SUCCESS")
    return ApiResponse(
        success=True,
        data={"message": "Your profile, assessments, and all associated evidence have been permanently deleted."},
        request_id=req_id
    )
