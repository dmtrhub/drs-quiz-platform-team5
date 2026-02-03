from marshmallow import Schema, fields, validates, ValidationError
from marshmallow.fields import Field
import re

class EnumField(Field):

class UserUpdateSchema(Schema):
    first_name = fields.Str(required=False)
    last_name = fields.Str(required=False)
    birth_date = fields.Str(required=False, allow_none=True)

class RoleChangeSchema(Schema):
    role = fields.Str(required=True)

class UserResponseSchema(Schema):
    id = fields.Int()
    email = fields.Email()
    first_name = fields.Str()
    last_name = fields.Str()
    birth_date = fields.Date(allow_none=True)