import yaml
from flask import Blueprint

from core.blueprints.utils import required_user_type, success_response
from core.utils import init_db

admin_bp = Blueprint("admin", __name__)


# TODO this should be only enabled in debug, this is used to reset the database in unit tests
@admin_bp.route("/admin/debug/reload", methods=["GET"])
@required_user_type(["admin"])
def reset_db():
    with open("data/init.yaml") as f:
        init_data = yaml.safe_load(f)
        init_db(init_data)
        return success_response("db reset")
