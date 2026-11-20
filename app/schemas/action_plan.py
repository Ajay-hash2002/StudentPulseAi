from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class ActionPlanCreateRequest(BaseModel):
    goal_id: Optional[str] = None
    target_role: Optional[str] = None

class ActionPlanItemResponse(BaseModel):
    recommendation_id: str
    action_text: str
    reason: str
    evidence_refs: List[str]
    priority: str  # high, medium, low
    status: str    # todo, in_progress, done
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ActionPlanResponse(BaseModel):
    plan_id: str
    target_role: str
    summary_explanation: str
    explanation_source: str  # "Deterministic Rule-based Explainer" or "Explainable AI Provider"
    actions: List[ActionPlanItemResponse]
    progress_pct: float
    limitations: List[str]

class ActionStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(todo|in_progress|done)$")
