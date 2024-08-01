import re

from marshmallow import Schema, fields, ValidationError, post_load

from core.models import User

email_format = re.compile(
    r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|"
    r"\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]"
    r"|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f"
    r"\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+))"
)


def validate_password(value: str):
    requirements = [
        (len(value) >= 8, "Minimum 8 characters"),
        (re.search(r"[A-Z]", value) is not None, "At least one uppercase letter"),
        (re.search(r"[a-z]", value) is not None, "At least one lowercase letter"),
        (re.search(r"\d", value) is not None, "At least one digit"),
    ]

    failed_requirements = [msg for condition, msg in requirements if not condition]

    if failed_requirements:
        raise ValidationError(failed_requirements)


def validate_email(value: str):
    if not re.match(email_format, value):
        raise ValidationError("Invalid email format")


class BaseSchema(Schema):
    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)


class EmailSchema(BaseSchema):
    email = fields.String(required=True, validate=validate_email)


class PasswordSchema(BaseSchema):
    password = fields.String(required=True, validate=validate_password)


class RegisterCredentialsSchema(EmailSchema, PasswordSchema):
    name = fields.String(required=True)
    surname = fields.String(required=True)


class LoginCredentialsSchema(EmailSchema):
    password = fields.String(required=True)


class ResetPasswordRequestSchema(EmailSchema):
    pass


class ResetPasswordSchema(PasswordSchema):
    pass
