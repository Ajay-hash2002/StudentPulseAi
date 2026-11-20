from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Student
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, StudentProfile
from app.schemas.envelope import ApiResponse, ErrorDetail
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=ApiResponse)
def register_student(req: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    if not req.consent_given:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="CONSENT_REQUIRED", message="Consent is required to create a profile."),
            request_id=req_id
        )

    existing = db.query(Student).filter(Student.email == req.email.lower().strip()).first()
    if existing:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="EMAIL_EXISTS", message="An account with this email already exists."),
            request_id=req_id
        )

    now = datetime.now(timezone.utc)
    new_student = Student(
        student_id=str(uuid.uuid4()),
        display_name=req.display_name.strip(),
        email=req.email.lower().strip(),
        password_hash=hash_password(req.password),
        consent_given=True,
        consent_at=now,
        created_at=now
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    log_audit_event(db, actor_id=new_student.student_id, action_type="REGISTER", outcome="SUCCESS")

    token = create_access_token({"sub": new_student.student_id, "email": new_student.email})
    data = TokenResponse(
        access_token=token,
        token_type="bearer",
        student_id=new_student.student_id,
        display_name=new_student.display_name,
        email=new_student.email
    )
    return ApiResponse(success=True, data=data.model_dump(), request_id=req_id)

@router.post("/login", response_model=ApiResponse)
def login_student(req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    student = db.query(Student).filter(Student.email == req.email.lower().strip()).first()
    if not student or not verify_password(req.password, student.password_hash):
        log_audit_event(db, actor_id=req.email, action_type="LOGIN", outcome="FAILED")
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="INVALID_CREDENTIALS", message="Invalid email or password."),
            request_id=req_id
        )

    log_audit_event(db, actor_id=student.student_id, action_type="LOGIN", outcome="SUCCESS")
    token = create_access_token({"sub": student.student_id, "email": student.email})
    data = TokenResponse(
        access_token=token,
        token_type="bearer",
        student_id=student.student_id,
        display_name=student.display_name,
        email=student.email
    )
    return ApiResponse(success=True, data=data.model_dump(), request_id=req_id)
