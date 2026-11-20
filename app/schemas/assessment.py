from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class AssessmentCreate(BaseModel):
    assessment_type: str = Field(..., min_length=2, max_length=100)
    score_or_result: float = Field(..., ge=0, le=100)
    max_score: float = Field(100.0, gt=0)

class AssessmentResponse(BaseModel):
    assessment_id: str
    assessment_type: str
    score_or_result: float
    max_score: float
    completed_at: datetime

    model_config = ConfigDict(from_attributes=True)
