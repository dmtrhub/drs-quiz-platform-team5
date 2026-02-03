from marshmallow import Schema, fields, validates, ValidationError, EXCLUDE
from app.utils.validators import validate_password_strength, validate_email
from app.schemas.user_schema import UserResponseSchema

class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    birth_date = fields.Date(required=False, allow_none=True)
    gender = fields.String(required=False, allow_none=True)
    country = fields.String(required=False, allow_none=True)
    street = fields.String(required=False, allow_none=True)
    street_number = fields.String(required=False, allow_none=True)
    profile_image = fields.String(required=False, allow_none=True)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

class AuthResponseSchema(Schema):
    message = fields.Str()
    access_token = fields.Str(required=False)
    user = fields.Nested(UserResponseSchema)