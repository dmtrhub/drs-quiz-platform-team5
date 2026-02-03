from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from datetime import date, datetime
from typing import Optional, List
from enum import Enum
import re


class GenderEnum(str, Enum):
    """Enum for gender options"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class RoleEnum(str, Enum):
    """Enum for user roles"""
    PLAYER = "player"
    MODERATOR = "moderator"
    ADMIN = "admin"


class UserBaseDTO(BaseModel):
    """Base DTO for user data"""
    first_name: str = Field(..., min_length=2, max_length=50, description="First name")
    last_name: str = Field(..., min_length=2, max_length=50, description="Last name")
    email: EmailStr = Field(..., description="Email address")
    date_of_birth: date = Field(..., description="Date of birth (YYYY-MM-DD)")
    gender: GenderEnum = Field(..., description="Gender")
    country: str = Field(..., min_length=2, max_length=100, description="Country")
    street: str = Field(..., min_length=2, max_length=200, description="Street")
    street_number: str = Field(..., min_length=1, max_length=20, description="Street number")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None
        }


class UserRegisterDTO(UserBaseDTO):
    """DTO for user registration"""
    password: str = Field(..., min_length=8, max_length=100, description="Password")

    @field_validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @field_validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        """Validate date of birth"""
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))

        if age < 13:
            raise ValueError('You must be at least 13 years old')
        if age > 120:
            raise ValueError('Invalid date of birth')
        if v > today:
            raise ValueError('Date of birth cannot be in the future')
        return v


class UserLoginDTO(BaseModel):
    """DTO for user login"""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")

    class Config:
        from_attributes = True


class UserUpdateDTO(BaseModel):
    """DTO for updating user profile"""
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    country: Optional[str] = Field(None, min_length=2, max_length=100)
    street: Optional[str] = Field(None, min_length=2, max_length=200)
    street_number: Optional[str] = Field(None, min_length=1, max_length=20)

    @field_validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        """Validate date of birth for update"""
        if v is not None:
            today = date.today()
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))

            if age < 13:
                raise ValueError('You must be at least 13 years old')
            if age > 120:
                raise ValueError('Invalid date of birth')
            if v > today:
                raise ValueError('Date of birth cannot be in the future')
        return v

    class Config:
        from_attributes = True


class UserResponseDTO(BaseModel):
    """DTO for user response"""
    id: int
    first_name: str
    last_name: str
    email: str
    date_of_birth: date
    gender: str
    country: str
    street: str
    street_number: str
    profile_image: Optional[str] = None
    profile_image_url: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    failed_login_attempts: int = 0
    is_login_blocked: bool = False
    blocked_time_remaining: int = 0

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None
        }

    @classmethod
    def from_user_model(cls, user):
        """Create DTO from User model"""
        return cls(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            date_of_birth=user.date_of_birth,
            gender=user.gender,
            country=user.country,
            street=user.street,
            street_number=user.street_number,
            profile_image=user.profile_image,
            profile_image_url=f'/api/auth/profile/image/{user.profile_image}' if user.profile_image else None,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            failed_login_attempts=user.failed_login_attempts,
            is_login_blocked=user.is_login_blocked(),
            blocked_time_remaining=user.get_blocked_time_remaining()
        )


class PasswordChangeDTO(BaseModel):
    """DTO for changing password"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

    @field_validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @model_validator(mode='after')
    def validate_passwords_not_equal(self):
        """Validate that new password is different from current"""
        if self.current_password == self.new_password:
            raise ValueError('New password must be different from current password')
        return self

    class Config:
        from_attributes = True


class UserRoleDTO(BaseModel):
    """DTO for changing user role"""
    role: RoleEnum = Field(..., description="New role for the user")

    class Config:
        from_attributes = True


class UserStatsDTO(BaseModel):
    """DTO for user statistics"""
    total_users: int
    new_users_last_30_days: int
    blocked_users: int
    roles: dict

    class Config:
        from_attributes = True