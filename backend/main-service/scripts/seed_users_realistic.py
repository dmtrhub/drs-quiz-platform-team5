import os
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / '.env')

from app import create_app, db
from app.models.user import User, RoleEnum
from app.utils.password_utils import hash_password


@dataclass(frozen=True)
class UserProfile:
    user_id: int
    first_name: str
    last_name: str
    email: str
    role: RoleEnum


USERS = [
    UserProfile(5101, 'John', 'Gotti', 'john.gotti@quizplatform.com', RoleEnum.MODERATOR),
    UserProfile(5102, 'Sarah', 'Connor', 'sarah.connor@quizplatform.com', RoleEnum.MODERATOR),
    UserProfile(5103, 'Michael', 'Corleone', 'michael.corleone@quizplatform.com', RoleEnum.MODERATOR),
    UserProfile(5104, 'Emma', 'Watson', 'emma.watson@quizplatform.com', RoleEnum.PLAYER),
    UserProfile(5105, 'David', 'Beckham', 'david.beckham@quizplatform.com', RoleEnum.PLAYER),
    UserProfile(5106, 'Olivia', 'Wilde', 'olivia.wilde@quizplatform.com', RoleEnum.PLAYER),
    UserProfile(5107, 'Ethan', 'Hawke', 'ethan.hawke@quizplatform.com', RoleEnum.PLAYER),
    UserProfile(5108, 'Amelia', 'Earhart', 'amelia.earhart@quizplatform.com', RoleEnum.PLAYER),
    UserProfile(5109, 'Daniel', 'Craig', 'daniel.craig@quizplatform.com', RoleEnum.PLAYER),
    UserProfile(5110, 'Sophia', 'Loren', 'sophia.loren@quizplatform.com', RoleEnum.PLAYER),
    UserProfile(5111, 'Liam', 'Neeson', 'liam.neeson@quizplatform.com', RoleEnum.PLAYER),
    UserProfile(5112, 'Ava', 'Gardner', 'ava.gardner@quizplatform.com', RoleEnum.PLAYER),
    UserProfile(5113, 'Noah', 'Webster', 'noah.webster@quizplatform.com', RoleEnum.PLAYER),
    UserProfile(5114, 'Nina', 'Simone', 'nina.simone@quizplatform.com', RoleEnum.PLAYER),
    UserProfile(5115, 'Oscar', 'Isaac', 'oscar.isaac@quizplatform.com', RoleEnum.PLAYER),
]


def build_user(profile: UserProfile, password_hash_value: str, force_auto_id: bool = False) -> User:
    kwargs = {
        'email': profile.email,
        'password_hash': password_hash_value,
        'first_name': profile.first_name,
        'last_name': profile.last_name,
        'role': profile.role,
        'country': 'USA',
        'gender': 'Prefer not to say',
        'birth_date': date(1990, 1, 1),
        'street': 'Quiz Street',
        'street_number': '1',
    }
    if not force_auto_id:
        kwargs['id'] = profile.user_id
    return User(**kwargs)


def seed_users() -> None:
    default_password = os.environ.get('SEED_REAL_USERS_PASSWORD', 'QuizUser123!')
    password_hash_value = hash_password(default_password)

    inserted = 0
    updated = 0
    skipped = 0

    moderator_map = {}

    for profile in USERS:
        existing_by_email = User.query.filter_by(email=profile.email).first()
        if existing_by_email:
            existing_by_email.first_name = profile.first_name
            existing_by_email.last_name = profile.last_name
            existing_by_email.role = profile.role
            existing_by_email.country = existing_by_email.country or 'USA'
            existing_by_email.gender = existing_by_email.gender or 'Prefer not to say'
            existing_by_email.birth_date = existing_by_email.birth_date or date(1990, 1, 1)
            existing_by_email.street = existing_by_email.street or 'Quiz Street'
            existing_by_email.street_number = existing_by_email.street_number or '1'
            if not existing_by_email.password_hash:
                existing_by_email.password_hash = password_hash_value
            updated += 1
            if profile.role == RoleEnum.MODERATOR:
                moderator_map[profile.email] = existing_by_email.id
            continue

        existing_by_id = db.session.get(User, profile.user_id)
        if existing_by_id and existing_by_id.email != profile.email:
            # Keep id collision safe by falling back to auto-generated id.
            db.session.add(build_user(profile, password_hash_value, force_auto_id=True))
            inserted += 1
            skipped += 1
            continue

        db.session.add(build_user(profile, password_hash_value))
        inserted += 1
        if profile.role == RoleEnum.MODERATOR:
            moderator_map[profile.email] = profile.user_id

    db.session.commit()

    db.session.execute(
        db.text(
            "SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE(MAX(id), 1)) FROM users"
        )
    )
    db.session.commit()

    # Refresh moderator map from DB to print authoritative ids.
    for profile in USERS:
        if profile.role == RoleEnum.MODERATOR:
            current = User.query.filter_by(email=profile.email).first()
            if current:
                moderator_map[profile.email] = current.id

    print(f"[SEED USERS] Inserted={inserted}, Updated={updated}, IdCollisions={skipped}")
    print('[SEED USERS] Moderators:')
    for email, user_id in sorted(moderator_map.items()):
        print(f"  - {email}: id={user_id}")


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_users()
