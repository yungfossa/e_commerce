from flask import Blueprint, jsonify

errors_bp = Blueprint("errors", __name__)


@errors_bp.app_errorhandler(400)
def bad_request(error):
    """
    Handle 400 Bad Request errors.

    Args:
        error: The error object containing details about the bad request.

    Returns:
        tuple: A tuple containing a JSON response with error details and a 400 status code.
    """
    return (
        jsonify({"error": "bad request", "message": str(error)}),
        400,
    )


@errors_bp.app_errorhandler(401)
def unauthorized(error):
    """
    Handle 401 Unauthorized errors.

    Args:
        error: The error object containing details about the unauthorized access.

    Returns:
        tuple: A tuple containing a JSON response with error details and a 401 status code.
    """
    return (
        jsonify({"error": "unauthorized", "message": str(error)}),
        401,
    )


@errors_bp.app_errorhandler(403)
def forbidden(error):
    """
    Handle 403 Forbidden errors.

    Args:
        error: The error object containing details about the forbidden access.

    Returns:
        tuple: A tuple containing a JSON response with error details and a 403 status code.
    """
    return (
        jsonify({"error": "forbidden", "message": str(error)}),
        403,
    )


@errors_bp.app_errorhandler(404)
def not_found(error):
    """
    Handle 404 Not Found errors.

    Args:
        error: The error object containing details about the resource not found.

    Returns:
        tuple: A tuple containing a JSON response with error details and a 404 status code.
    """
    return (
        jsonify({"error": "not found", "message": str(error)}),
        404,
    )


@errors_bp.app_errorhandler(500)
def internal_server_error():
    """
    Handle 500 Internal Server errors.

    Returns:
        tuple: A tuple containing a JSON response with a generic error message and a 500 status code.
    """
    return (
        jsonify(
            {
                "error": "internal server error",
                "message": "an unexpected error occurred",
            }
        ),
        500,
    )


@errors_bp.app_errorhandler(Exception)
def handle_exception(error):
    """
    Handle any unhandled exceptions.

    Args:
        error: The exception object.

    Returns:
        tuple: A tuple containing a JSON response with error details and a 500 status code.
    """
    return (
        jsonify({"error": "server error", "message": str(error)}),
        500,
    )


# This module defines error handlers for common HTTP status codes and exceptions.
# It provides a consistent JSON response format for various types of errors that may occur in the application.

# Key features:
# - Handles common HTTP error codes (400, 401, 403, 404, 500)
# - Provides a catch-all handler for unhandled exceptions
# - Returns JSON-formatted error responses for easy parsing by API clients

# Usage:
# These error handlers are automatically invoked by Flask when the corresponding
# errors occur in the application. They ensure that all errors are returned in
# a consistent JSON format, which is particularly useful for API development.

# Security considerations:
# - The internal_server_error handler returns a generic message to avoid exposing
#   sensitive information about the server's internal state.
# - The handle_exception function should be used cautiously in production, as it
#   may expose sensitive error details. Consider logging the full error and
#   returning a more generic message in production environments.

# Note: This error handling approach provides a good foundation for API error responses,
# but may need to be extended or modified based on specific application requirements.
