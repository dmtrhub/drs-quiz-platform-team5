from marshmallow import Schema, fields, validates, ValidationError
from marshmallow.fields import Field
import re

class EnumField(Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        if hasattr(value, 'value'):
            return value.value
        return str(value)


class UserUpdateSchema(Schema):
    first_name = fields.Str(required=False)
    last_name = fields.Str(required=False)
    birth_date = fields.Str(required=False, allow_none=True)
    gender = fields.Str(required=False, allow_none=True)
    country = fields.Str(required=False, allow_none=True)
    street = fields.Str(required=False, allow_none=True)
    street_number = fields.Str(required=False, allow_none=True)
    profile_image = fields.Str(required=False, allow_none=True)
    current_password = fields.Str(required=False, allow_none=True)
    new_password = fields.Str(required=False, allow_none=True)

    @validates('profile_image')
    def validate_profile_image(self, value):
        if value and not value.startswith('data:image/'):
            # If it's not a base64 image, it should be a URL
            if not re.match(r'^https?://', value):
                raise ValidationError('Profile image must be a valid URL or base64 image')
        return value


class RoleChangeSchema(Schema):
    role = fields.Str(required=True)

class UserResponseSchema(Schema):
    id = fields.Int()
    email = fields.Email()
    first_name = fields.Str()
    last_name = fields.Str()
    birth_date = fields.Date(allow_none=True)
    gender = fields.Str(allow_none=True)
    country = fields.Str(allow_none=True)
    street = fields.Str(allow_none=True)
    street_number = fields.Str(allow_none=True)
    profile_image = fields.Str(allow_none=True)
    role = EnumField()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()