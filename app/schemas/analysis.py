from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SkillGapRequest(BaseModel):
    goal_id: Optional[str] = None
    target_role: Optional[str] = None

class SkillGapItem(BaseModel):
    skill: str
    required_level: int
    observed_level: Optional[int] = None
    level_label: str
    status: str  # strong, weak, missing_evidence
    reason: str
    evidence_refs: List[str]

class SkillGapResponse(BaseModel):
    target_role: str
    total_required_skills: int
    strong_count: int
    weak_count: int
    missing_count: int
    gaps: List[SkillGapItem]
    generated_at: datetime

class CriterionBreakdown(BaseModel):
    criterion: str
    weight: float
    achieved_score: float
    max_possible: float
    description: str

class ReadinessResponse(BaseModel):
    target_role: str
    readiness_score: float
    evidence_coverage_pct: float
    readiness_level: str  # High Readiness, Moderate Readiness, Foundation Stage, Needs Baseline Evidence
    criteria_breakdown: List[CriterionBreakdown]
    strengths: List[str]
    critical_gaps: List[str]
    limitations: str
    generated_at: datetime

class ProjectReadinessResponse(BaseModel):
    target_role: str
    completed_projects_count: int
    demonstrated_skills: List[str]
    missing_role_capabilities: List[str]
    project_coverage_pct: float
    readiness_summary: str

class InterviewReadinessResponse(BaseModel):
    communication_score: Optional[float]
    mock_practices_count: int
    presentation_evidence_count: int
    interview_readiness_level: str
    recommended_practice_topics: List[str]
