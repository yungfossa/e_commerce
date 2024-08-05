import re

from marshmallow import Schema, fields, ValidationError, post_load

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


class EmailSchema(Schema):
    email = fields.String(required=True, validate=validate_email)


class PasswordSchema(Schema):
    password = fields.String(required=True, validate=validate_password)


class RegisterCredentialsSchema(EmailSchema, PasswordSchema):
    name = fields.String(required=True)
    surname = fields.String(required=True)

    @post_load
    def get_validated_register_credentials(self, data, **args):
        return {
            "email": data.get("email"),
            "password": data.get("password"),
            "name": data.get("name"),
            "surname": data.get("surname"),
        }


class LoginCredentialsSchema(EmailSchema):
    password = fields.String(required=True)

    @post_load
    def get_validated_login_credentials(self, data, **args):
        return {
            "email": data.get("email"),
            "password": data.get("password"),
        }


class ResetPasswordRequestSchema(EmailSchema):
    @post_load
    def get_validated_email(self, data, **args):
        return {
            "email": data.get("email"),
        }


class ResetPasswordSchema(PasswordSchema):
    @post_load
    def get_validated_password(self, data, **args):
        return {
            "password": data.get("password"),
        }
