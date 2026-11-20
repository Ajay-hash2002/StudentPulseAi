import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Student(Base):
    __tablename__ = "students"

    student_id = Column(String(36), primary_key=True, default=generate_uuid)
    display_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    consent_given = Column(Boolean, default=False, nullable=False)
    consent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    evidence = relationship("StudentSkillEvidence", back_populates="student", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="student", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="student", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="student", cascade="all, delete-orphan")
    career_goals = relationship("CareerGoal", back_populates="student", cascade="all, delete-orphan")
    action_plans = relationship("ActionPlanItem", back_populates="student", cascade="all, delete-orphan")

class Skill(Base):
    __tablename__ = "skills"

    skill_id = Column(String(50), primary_key=True)
    skill_name = Column(String(80), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)  # Technical, Soft, Tools

    evidence_records = relationship("StudentSkillEvidence", back_populates="skill")

class StudentSkillEvidence(Base):
    __tablename__ = "student_skill_evidence"

    evidence_id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(String(50), ForeignKey("skills.skill_id", ondelete="CASCADE"), nullable=False, index=True)
    source_type = Column(String(50), nullable=False)  # assessment, project, certification, interview, self_reported
    evidence_reference = Column(String(255), nullable=False)
    observed_level = Column(Integer, nullable=False, default=1)  # 0 to 4
    date = Column(DateTime, default=utc_now, nullable=False)

    student = relationship("Student", back_populates="evidence")
    skill = relationship("Skill", back_populates="evidence_records")

class Assessment(Base):
    __tablename__ = "assessments"

    assessment_id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_type = Column(String(100), nullable=False)
    score_or_result = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False, default=100.0)
    completed_at = Column(DateTime, default=utc_now, nullable=False)

    student = relationship("Student", back_populates="assessments")

class Project(Base):
    __tablename__ = "projects"

    project_id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    skills_used = Column(Text, nullable=False)  # JSON-encoded array of skill names
    status = Column(String(30), nullable=False, default="in_progress")  # planned, in_progress, completed
    created_at = Column(DateTime, default=utc_now, nullable=False)

    student = relationship("Student", back_populates="projects")

class Certification(Base):
    __tablename__ = "certifications"

    certification_id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    issuer = Column(String(150), nullable=False)
    issue_date = Column(DateTime, default=utc_now, nullable=False)
    verification_reference = Column(String(255), nullable=True)

    student = relationship("Student", back_populates="certifications")

class CareerGoal(Base):
    __tablename__ = "career_goals"

    goal_id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    target_role = Column(String(100), nullable=False)
    target_date = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    student = relationship("Student", back_populates="career_goals")

class ActionPlanItem(Base):
    __tablename__ = "action_plan_items"

    recommendation_id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    goal_id = Column(String(36), nullable=True)
    action_text = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)
    evidence_refs = Column(Text, nullable=False, default="[]")  # JSON-encoded array of evidence ids/rules
    priority = Column(String(20), nullable=False, default="medium")  # high, medium, low
    status = Column(String(20), nullable=False, default="todo")  # todo, in_progress, done
    created_at = Column(DateTime, default=utc_now, nullable=False)

    student = relationship("Student", back_populates="action_plans")

class AuditEvent(Base):
    __tablename__ = "audit_events"

    event_id = Column(String(36), primary_key=True, default=generate_uuid)
    actor_id = Column(String(36), nullable=False)
    action_type = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=utc_now, nullable=False)
    outcome = Column(String(50), nullable=False)
