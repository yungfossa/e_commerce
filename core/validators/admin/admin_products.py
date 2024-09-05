from marshmallow import Schema, fields, post_load


class CategorySchema(Schema):
    category_title = fields.String(
        required=True, error_messages={"required": "Missing product category title"}
    )

    @post_load
    def get_validated_category_product(self, data, **kwargs):
        return {
            "title": data.get("category_title"),
        }


class AddProductSchema(Schema):
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
        return {
            "name": data.get("name"),
            "description": data.get("description"),
            "image_src": data.get("image_src"),
            "category": data.get("category_title"),
        }
