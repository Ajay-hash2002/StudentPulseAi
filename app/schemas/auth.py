from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class RegisterRequest(BaseModel):
    display_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    consent_given: bool = Field(..., description="Consent to store educational profile data")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenData(BaseModel):
    student_id: str
    email: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    student_id: str
    display_name: str
    email: str

class StudentProfile(BaseModel):
    student_id: str
    display_name: str
    email: str
    consent_given: bool
    consent_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
