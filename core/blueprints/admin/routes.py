import yaml
from flask import Blueprint, current_app

from core.blueprints.errors.handlers import handle_exception
from core.blueprints.utils import required_user_type, success_response
from core.utils import init_db

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/debug/reload", methods=["GET"])
@required_user_type(["admin"])
def reset_db():
    config_name = current_app.config["NAME"]

    if config_name != "development":
        return handle_exception(
            message="This endpoint is only available in development mode"
        )

    with open("data/init.yaml") as f:
        init_data = yaml.safe_load(f)
        init_db(init_data)
        return success_response("db reset")
