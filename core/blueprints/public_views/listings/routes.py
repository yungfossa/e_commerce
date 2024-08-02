from flask import Blueprint

from core.validators.seller.seller_listing import ReviewQuerySchema

listings_bp = Blueprint("listings", __name__)

validate_review_query = ReviewQuerySchema


@listings_bp.route("/listings/<string:listing_ulid>", methods=["POST"])
def get_listing(listing_ulid):
    """
    try:
        validated_data = validate_review_query.load(request.get_json())
    except ValidationError as err:
        return bad_request(err.messages)

    listing = (
        db.session.query(MVProductCategory, Listing)
        .join(Listing, Listing.product_id == MVProductCategory.product_id)
        .filter(Listing.id == listing_ulid)
        .first()
    )

    if not listing:
        return not_found(message="Listing not found")
    """
    return "Hello"
