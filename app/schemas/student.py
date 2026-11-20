from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class StudentUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=2, max_length=100)

class EvidenceCreate(BaseModel):
    skill_name: str = Field(..., min_length=1, max_length=80)
    source_type: str = Field(..., pattern="^(assessment|project|certification|interview|self_reported)$")
    evidence_reference: str = Field(..., min_length=3, max_length=255)
    observed_level: int = Field(..., ge=1, le=4, description="1=Beginner, 2=Basic, 3=Intermediate, 4=Advanced")

class EvidenceResponse(BaseModel):
    evidence_id: str
    skill_id: str
    skill_name: str
    source_type: str
    evidence_reference: str
    observed_level: int
    date: datetime

    model_config = ConfigDict(from_attributes=True)

class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    description: str = Field(..., min_length=5)
    skills_used: List[str] = Field(..., min_length=1)
    status: str = Field("in_progress", pattern="^(planned|in_progress|completed)$")

class ProjectResponse(BaseModel):
    project_id: str
    title: str
    description: str
    skills_used: List[str]
    status: str
    created_at: datetime

class CertificationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    issuer: str = Field(..., min_length=2, max_length=150)
    verification_reference: Optional[str] = Field(None, max_length=255)

class CertificationResponse(BaseModel):
    certification_id: str
    name: str
    issuer: str
    issue_date: datetime
    verification_reference: Optional[str]

class CareerGoalCreate(BaseModel):
    target_role: str = Field(..., min_length=2, max_length=100)
    target_date: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None

class CareerGoalResponse(BaseModel):
    goal_id: str
    target_role: str
    target_date: Optional[str]
    notes: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
