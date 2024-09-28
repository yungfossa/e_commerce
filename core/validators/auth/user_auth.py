import re

from marshmallow import Schema, ValidationError, fields, post_load

# Complex regex pattern for validating email addresses
email_format = re.compile(
    r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|"
    r"\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]"
    r"|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f"
    r"\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+))"
)


def validate_password(value: str):
    """
    Validate the password against security requirements.

    Args:
        value (str): The password to validate.

    Raises:
        ValidationError: If the password doesn't meet the requirements.
    """
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
    """
    Validate the email format.

    Args:
        value (str): The email to validate.

    Raises:
        ValidationError: If the email format is invalid.
    """
    if not re.match(email_format, value):
        raise ValidationError("Invalid email format")


class EmailSchema(Schema):
    """Schema for validating email addresses."""

    email = fields.String(required=True, validate=validate_email)


class PasswordSchema(Schema):
    """Schema for validating passwords."""

    password = fields.String(required=True, validate=validate_password)


class RegisterCredentialsSchema(EmailSchema, PasswordSchema):
    """Schema for validating user registration data."""

    name = fields.String(required=True)
    surname = fields.String(required=True)

    @post_load
    def get_validated_register_credentials(self, data, **args):
        """Transform validated registration data."""
        return {
            "email": data.get("email"),
            "password": data.get("password"),
            "name": data.get("name"),
            "surname": data.get("surname"),
        }


class LoginCredentialsSchema(EmailSchema):
    """Schema for validating login credentials."""

    password = fields.String(required=True)

    @post_load
    def get_validated_login_credentials(self, data, **args):
        """Transform validated login data."""
        return {
            "email": data.get("email"),
            "password": data.get("password"),
        }


class ResetPasswordRequestSchema(EmailSchema):
    """Schema for validating password reset requests."""

    @post_load
    def get_validated_email(self, data, **args):
        """Transform validated email data for password reset."""
        return {
            "email": data.get("email"),
        }


class ResetPasswordSchema(PasswordSchema):
    """Schema for validating new passwords in reset password process."""

    @post_load
    def get_validated_password(self, data, **args):
        """Transform validated password data for password reset."""
        return {
            "password": data.get("password"),
        }
