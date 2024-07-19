from flask import Blueprint, jsonify

errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'bad Request', 'message': str(error)}), 400

@errors_bp.app_errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'unauthorized', 'message': str(error)}), 401

@errors_bp.app_errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'forbidden', 'message': str(error)}), 403

@errors_bp.app_errorhandler(404)
def not_found(error):
    return jsonify({'error': 'not found', 'message': str(error)}), 404

@errors_bp.app_errorhandler(500)
def internal_server_error():
    return jsonify({'error': 'internal server error', 'message': 'An unexpected error occurred'}), 500

@errors_bp.app_errorhandler(Exception)
def handle_exception(error):
    return jsonify({'error': 'server error', 'message': str(error)}), 500

