from typing import Any, Optional
from pydantic import BaseModel, Field

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None

class ApiResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None
    request_id: Optional[str] = None
