from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from .user_dto import UserResponseDTO


class BaseDTO(BaseModel):
    """Base DTO class"""

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class TokenDTO(BaseDTO):
    """DTO for authentication tokens"""
    access_token: str = Field(..., description="Access token for API calls")
    refresh_token: str = Field(..., description="Refresh token for getting new access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(default=3600, description="Token expiration in seconds")


class AuthResponseDTO(BaseDTO):
    """DTO for authentication response"""
    message: str = Field(..., description="Response message")
    user: UserResponseDTO = Field(..., description="User data")
    tokens: TokenDTO = Field(..., description="Authentication tokens")


class RefreshTokenDTO(BaseDTO):
    """DTO for refresh token response"""
    access_token: str = Field(..., description="New access token")


class LogoutResponseDTO(BaseDTO):
    """DTO for logout response"""
    message: str = Field(..., description="Logout message")


class ProfileImageResponseDTO(BaseDTO):
    """DTO for profile image upload response"""
    message: str = Field(..., description="Response message")
    image_url: str = Field(..., description="URL to the uploaded image")
    filename: str = Field(..., description="Name of the uploaded file")


class LoginAttemptDTO(BaseDTO):
    """DTO for login attempt records"""
    id: int
    email: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool
    attempted_at: datetime

    @classmethod
    def from_login_attempt_model(cls, attempt):
        """Create DTO from LoginAttempt model"""
        return cls(
            id=attempt.id,
            email=attempt.email,
            ip_address=attempt.ip_address,
            user_agent=attempt.user_agent,
            success=attempt.success,
            attempted_at=attempt.attempted_at
        )