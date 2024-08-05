from flask import Blueprint

from core.blueprints.utils import required_user_type, success_response
from core.models import User

admin_users_bp = Blueprint("admin_users", __name__)


@admin_users_bp.route("/admin/users", methods=["GET"])
@required_user_type(["admin"])
def get_users():
    us = User.query.all()

    return success_response(
        message="Users", data=[u.to_dict(rules=("-password",)) for u in us]
    )
