from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class BaseDTO(BaseModel):
    """Base DTO class with common methods"""

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

    def to_dict(self) -> dict:
        """Convert DTO to dictionary"""
        return self.model_dump(exclude_none=True)


class ErrorResponseDTO(BaseDTO):
    """DTO for error responses"""
    error: str
    message: str
    details: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Validation Error",
                "message": "Invalid input data",
                "details": {"field": "email", "error": "Invalid email format"},
                "timestamp": "2024-01-01T12:00:00"
            }
        }


class SuccessResponseDTO(BaseDTO):
    """DTO for success responses"""
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation successful",
                "data": {"id": 1, "name": "John"},
                "timestamp": "2024-01-01T12:00:00"
            }
        }