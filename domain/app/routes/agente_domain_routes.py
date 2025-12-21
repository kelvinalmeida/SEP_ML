from flask import Blueprint, jsonify

agente_domain_bp = Blueprint('agente_domain', __name__)

@agente_domain_bp.route('/domains/info', methods=['GET'])
def get_domain_info():
    # Dummy domain context
    context = {
        "description": "General Education Domain",
        "rules": ["Time limit: 60min", "Required: at least 1 tactic"]
    }
    return jsonify(context), 200
