import os
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / '.env')

from app import create_app, db
from app.models.user import User, RoleEnum
from app.utils.password_utils import hash_password


def seed_admin():
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@quizplatform.com')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    admin_first_name = os.environ.get('ADMIN_FIRST_NAME', 'System')
    admin_last_name = os.environ.get('ADMIN_LAST_NAME', 'Admin')

    if not admin_password:
        raise RuntimeError('ADMIN_PASSWORD is required for admin seeding')

    existing = User.query.filter_by(email=admin_email).first()

    if existing:
        if existing.role != RoleEnum.ADMIN:
            existing.role = RoleEnum.ADMIN
            db.session.commit()
            print(f"[SEED] Elevated existing user to ADMIN: {admin_email}")
        else:
            print(f"[SEED] Admin already exists: {admin_email}")
        return

    admin_user = User(
        email=admin_email,
        password_hash=hash_password(admin_password),
        first_name=admin_first_name,
        last_name=admin_last_name,
        role=RoleEnum.ADMIN,
    )

    db.session.add(admin_user)
    db.session.commit()

    print(f"[SEED] Created admin user: {admin_email}")


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_admin()
