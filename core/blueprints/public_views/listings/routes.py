from flask import Blueprint

listings_bp = Blueprint("listings", __name__)


@listings_bp.route("/listings/<string:listing_ulid>", methods=["POST"])
def get_listing(listing_ulid):
    return "Hello"
