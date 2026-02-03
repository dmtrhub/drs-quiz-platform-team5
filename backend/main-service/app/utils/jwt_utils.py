from flask_jwt_extended import create_access_token, decode_token
from datetime import timedelta


def generate_token(user_id, email, role, first_name=None, last_name=None):
    additional_claims = {
        "email": email,
        "role": role,
        "first_name": first_name or "",
        "last_name": last_name or ""
    }
    access_token = create_access_token(
        identity=str(user_id),
        additional_claims=additional_claims,
        expires_delta=timedelta(hours=3)
    )
    return access_token


def decode_jwt_token(token):
    try:
        payload = decode_token(token)
        return payload
    except Exception as e:
        return None
