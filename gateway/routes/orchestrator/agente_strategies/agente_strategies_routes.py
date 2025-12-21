from flask import Blueprint, request, jsonify
import requests
from routes.services_routs import DOMAIN_URL, STRATEGIES_URL

orchestrator_bp = Blueprint('orchestrator', __name__)

@orchestrator_bp.route('/strategies/orchestrate_validation', methods=['POST'])
def orchestrate_validation():
    try:
        strategy_data = request.get_json()

        # 1. Get Domain Info
        try:
            domain_response = requests.get(f"{DOMAIN_URL}/domains/info")
            domain_info = domain_response.json() if domain_response.status_code == 200 else {}
        except Exception:
            domain_info = {}

        # 2. Send to Worker (Strategies)
        payload = {
            "strategy": strategy_data,
            "domain_info": domain_info
        }

        worker_response = requests.post(f"{STRATEGIES_URL}/strategies/validate", json=payload)

        if worker_response.status_code == 200:
            return jsonify(worker_response.json()), 200
        else:
            return jsonify({"error": "Validation failed", "details": worker_response.text}), worker_response.status_code

    except Exception as e:
        return jsonify({"error": "Orchestration error", "details": str(e)}), 500
