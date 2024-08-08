import phonenumbers
from marshmallow import Schema, fields, post_load, validates
from marshmallow.validate import ValidationError


class EditProfileSchema(Schema):
    phone_number = fields.String(required=False)
    profile_img = fields.String(required=False)

    @validates("phone_number")
    def validate_phone_number(self, value):
        try:
            p = phonenumbers.parse(value)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError("Invalid phone number")

    @post_load
    def get_validated_customer_profile(self, data, **kwargs):
        return {
            "phone_number": data.get("phone_number"),
            "profile_img": data.get("profile_img"),
        }


class DeleteProfileSchema(Schema):
    reason = fields.String(required=True, error_messages={"required": "Missing reason"})

    @post_load
    def get_validated_delete_req(self, data, **kwargs):
        return {
            "reason": data.get("reason"),
        }


class EditSellerProfileSchema(EditProfileSchema):
    company_name = fields.String(required=False)

    @post_load
    def get_validated_seller_profile(self, data, **kwargs):
        return {
            "phone_number": data.get("phone_number"),
            "profile_img": data.get("profile_img"),
            "company_name": data.get("company_name"),
        }


class EditCustomerProfileSchema(EditProfileSchema):
    pass
