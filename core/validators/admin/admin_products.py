from marshmallow import Schema, fields, post_load


class CategorySchema(Schema):
    """
    Schema for validating product category data.

    This schema is used to validate and deserialize input data
    for creating or updating product categories.
    """

    category_title = fields.String(
        required=True, error_messages={"required": "Missing product category title"}
    )

    @post_load
    def get_validated_category_product(self, data, **kwargs):
        """
        Post-load hook to transform validated data into the desired format.

        This method is automatically called after successful data validation.
        It restructures the validated data into the format expected by the application.

        Args:
            data (dict): The validated data.
            **kwargs: Additional keyword arguments passed to the method.

        Returns:
            dict: A dictionary with the 'title' key containing the category title.
        """
        return {
            "title": data.get("category_title"),
        }


class AddProductSchema(Schema):
    """
    Schema for validating product data when adding a new product.

    This schema is used to validate and deserialize input data
    for creating new products in the admin interface.
    """

    name = fields.String(
        required=True, error_messages={"required": "Missing product name"}
    )
    description = fields.String(
        required=True, error_messages={"required": "Missing product description"}
    )
    image_src = fields.String(
        required=True, error_messages={"required": "Missing product image"}
    )
    category_title = fields.String(
        required=True, error_messages={"required": "Missing product category title"}
    )

    @post_load
    def get_validated_product(self, data, **kwargs):
        """
        Post-load hook to transform validated data into the desired format.

        This method is automatically called after successful data validation.
        It restructures the validated data into the format expected by the application.

        Args:
            data (dict): The validated data.
            **kwargs: Additional keyword arguments passed to the method.

        Returns:
            dict: A dictionary containing the validated and formatted product data.
        """
        return {
            "name": data.get("name"),
            "description": data.get("description"),
            "image_src": data.get("image_src"),
            "category": data.get("category_title"),
        }


# This module defines Marshmallow schemas for validating and deserializing
# input data related to product categories and products in the admin interface.

# Key components:
# 1. CategorySchema: Used for validating product category data.
# 2. AddProductSchema: Used for validating data when adding a new product.

# Both schemas include post_load hooks that transform the validated data
# into the format expected by the application's business logic.

# These schemas help ensure data integrity and provide clear error messages
# when required fields are missing, improving the robustness of the admin interface.
