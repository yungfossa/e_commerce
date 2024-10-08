import requests
from marshmallow import Schema, ValidationError, fields, post_load, validates_schema
from marshmallow.validate import Length, OneOf, Range

INVALID_ARG_KEY = "invalid arg"
ORDER_BY_OPTIONS = ["purchased_at", "price"]
NOMINATIM_API_URL = "https://nominatim.openstreetmap.org/search"


class OrderCreationSchema(Schema):
    """
    Schema for validating order creation data.

    This schema ensures that all required address fields are provided
    and validates the address using an external geocoding service.
    """

    address_street = fields.String(
        required=True,
        validate=Length(min=1),
        error_messages={INVALID_ARG_KEY: "Invalid address street"},
    )
    address_city = fields.String(
        required=True,
        validate=Length(min=1),
        error_messages={INVALID_ARG_KEY: "Invalid address city"},
    )
    address_state = fields.String(
        required=True,
        validate=Length(min=1),
        error_messages={INVALID_ARG_KEY: "Invalid address state"},
    )
    address_country = fields.String(
        required=True,
        validate=Length(min=1),
        error_messages={INVALID_ARG_KEY: "Invalid address country"},
    )
    address_postal_code = fields.String(
        required=True,
        validate=Length(min=1),
        error_messages={INVALID_ARG_KEY: "Invalid address postal code"},
    )

    @validates_schema
    def validate_address(self, data, **kwargs):
        """
        Validate the complete address using the Nominatim geocoding service.

        Args:
            data (dict): The address data to validate.

        Raises:
            ValidationError: If the address is invalid or not found.
        """
        response = requests.get(
            NOMINATIM_API_URL,
            params={
                "street": data["address_street"],
                "city": data["address_city"],
                "state": data["address_state"],
                "country": data["address_country"],
                "postalcode": data["address_postal_code"],
                "format": "json",
            },
            headers={"User-Agent": "ShopSphere/1.0"},
        )
        result = response.json()
        if not result:
            raise ValidationError("Invalid address")

    @post_load
    def get_validated_order_data(self, data, **kwargs):
        """Transform validated order data into the expected format."""
        return {
            "address_street": data.get("address_street"),
            "address_city": data.get("address_city"),
            "address_state": data.get("address_state"),
            "address_country": data.get("address_country"),
            "address_postal_code": data.get("address_postal_code"),
        }


class OrderSummaryFilterSchema(Schema):
    """
    Schema for validating order summary filter parameters.

    This schema defines and validates various filter options for retrieving order summaries,
    including pagination, sorting, and status filtering.
    """

    offset = fields.Integer(
        required=False,
        missing=0,
        validate=Range(min=0),
        error_messages={INVALID_ARG_KEY: "Invalid offset value"},
    )
    limit = fields.Integer(
        required=False,
        missing=10,
        validate=Range(min=1, max=100),
        error_messages={INVALID_ARG_KEY: "Invalid limit value"},
    )
    order_by = fields.String(
        required=False,
        missing="purchased_at",
        validate=OneOf(ORDER_BY_OPTIONS),
        error_messages={INVALID_ARG_KEY: "Invalid order_by filter"},
    )
    order_direction = fields.String(
        required=False,
        missing="desc",
        validate=OneOf(["asc", "desc"]),
        error_messages={INVALID_ARG_KEY: "Invalid order direction"},
    )
    status = fields.String(
        required=False,
        missing="pending",
        validate=OneOf(["pending", "shipped", "delivered", "cancelled"]),
        error_messages={INVALID_ARG_KEY: "Invalid order status"},
    )

    @post_load
    def get_validated_order_history_filters(self, data, **kwargs):
        """Transform validated filter data into the expected format."""
        return {
            "offset": data.get("offset"),
            "limit": data.get("limit"),
            "order_by": data.get("order_by"),
            "order_direction": data.get("order_direction"),
            "status": data.get("status"),
        }
