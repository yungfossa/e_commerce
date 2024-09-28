import yaml
from flask import Blueprint, current_app

from core.blueprints.errors.handlers import handle_exception
from core.blueprints.utils import required_user_type, success_response
from core.utils import init_db

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/debug/reload", methods=["GET"])
@required_user_type(["admin"])
def reset_db():
    """
    Reset the database to its initial state.

    This endpoint allows administrators to reset the database to its initial state
    using the data from the 'data/init.yaml' file. This operation is only available
    in the development environment.

    Returns:
        A JSON response indicating success or failure of the database reset operation.

    Raises:
        Exception: If the operation is attempted in a non-development environment.
    """
    config_name = current_app.config["NAME"]

    if config_name != "development":
        return handle_exception(
            message="This endpoint is only available in development mode"
        )

    with open("data/init.yaml") as f:
        init_data = yaml.safe_load(f)
        init_db(init_data)
        return success_response("db reset")


# This module defines an administrative endpoint for database management.

# Key features:
# - Provides a method to reset the database to its initial state
# - Restricted to admin users only
# - Only available in the development environment

# The reset_db function:
# 1. Checks if the current environment is development
# 2. Loads initial data from a YAML file
# 3. Calls the init_db function to reset the database with this data

# Security considerations:
# - The endpoint is protected by the @required_user_type decorator, ensuring only admins can access it
# - An additional check ensures this operation can only be performed in the development environment

# Note: This endpoint should never be exposed in a production environment, as it could lead to data loss.

# Usage:
# This endpoint is primarily intended for development and testing purposes, allowing quick reset of the database to a known state.
