from app import db
from datetime import datetime

class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), ondelete='CASCADE', nullable=False)
    email = db.Column(db.String(120))
    success = db.Column(db.Boolean, nullable=False)
    ip_address = db.Column(db.String(50))
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow) 

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email': self.email,
            'success': self.success,
            'ip_address': self.ip_address,
            'attempted_at': self.attempted_at.isoformat() if self.attempted_at else None
        }