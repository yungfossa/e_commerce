import phonenumbers
from marshmallow import Schema, fields, post_load, validates
from marshmallow.validate import ValidationError


class EditProfileSchema(Schema):
    """
    Base schema for editing user profiles.

    This schema provides common fields and validation for both customer and seller profiles.
    """

    phone_number = fields.String(required=False)
    profile_img = fields.String(required=False)

    @validates("phone_number")
    def validate_phone_number(self, value):
        """
        Validate the phone number using the phonenumbers library.

        Args:
            value (str): The phone number to validate.

        Raises:
            ValidationError: If the phone number is invalid.
        """
        try:
            p = phonenumbers.parse(value)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError("Invalid phone number")

    @post_load
    def get_validated_customer_profile(self, data, **kwargs):
        """Transform validated profile data into the expected format."""
        return {
            "phone_number": data.get("phone_number"),
            "profile_img": data.get("profile_img"),
        }


class DeleteProfileSchema(Schema):
    """
    Schema for validating profile deletion requests.
    """

    reason = fields.String(required=True, error_messages={"required": "Missing reason"})

    @post_load
    def get_validated_delete_req(self, data, **kwargs):
        """Transform validated deletion request data into the expected format."""
        return {
            "reason": data.get("reason"),
        }


class EditSellerProfileSchema(EditProfileSchema):
    """
    Schema for editing seller profiles.

    This schema extends EditProfileSchema to include seller-specific fields.
    """

    company_name = fields.String(required=False)

    @post_load
    def get_validated_seller_profile(self, data, **kwargs):
        """Transform validated seller profile data into the expected format."""
        return {
            "phone_number": data.get("phone_number"),
            "profile_img": data.get("profile_img"),
            "company_name": data.get("company_name"),
        }


class EditCustomerProfileSchema(EditProfileSchema):
    """
    Schema for editing customer profiles.

    This schema extends EditProfileSchema without adding any additional fields.
    It's defined separately to allow for potential future customer-specific additions.
    """

    pass
