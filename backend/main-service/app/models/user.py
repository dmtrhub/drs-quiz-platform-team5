from app import db
from enum import Enum
from datetime import datetime


class RoleEnum(Enum):
    PLAYER = "PLAYER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date)
    gender = db.Column(db.String(20))
    country = db.Column(db.String(100))
    street = db.Column(db.String(255))
    street_number = db.Column(db.String(10))
    profile_image = db.Column(db.Text)
    role = db.Column(db.Enum(RoleEnum), default=RoleEnum.PLAYER)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'gender': self.gender,
            'country': self.country,
            'street': self.street,
            'street_number': self.street_number,
            'profile_image': self.profile_image,
            'role': self.role.value if self.role else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
