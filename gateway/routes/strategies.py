from flask import Blueprint, render_template, request, jsonify
from requests.exceptions import RequestException
import requests
from .services_routs import STRATEGIES_URL


strategy_bp = Blueprint("strategy", __name__)

@strategy_bp.route('/strategies/create', methods=['POST', 'GET'])
def create_strategy():
    if request.method == 'POST':
        # Get the form data
        name = request.form.get("name")
        tatics = request.form.getlist("tatics")
        times = request.form.getlist("times")
        description = request.form.getlist("description")

        # Junta tática + tempo
        tatics_with_times = [
            {"name": tatics[i], "time": int(times[i]), "description": description[i]}
            for i in range(len(tatics))
        ]

        strategy = {"name": name, "tatics": tatics_with_times}
        
        try:
            response = requests.post(f"{STRATEGIES_URL}/strategies/create", json=strategy)
            if response.status_code == 200:
                json_response = response.json()
                return jsonify(json_response), 200
            else:
                return jsonify({"error": "Failed to create strategy", "details": response.text}), response.status_code
        except RequestException as e:
            return jsonify({"error": "Strategies service unavailable", "details": str(e)}), 503
    
    return render_template("./strategies/create_strategy.html")



@strategy_bp.route('/strategies', methods=['GET'])
def get_strategies(current_user=None):
    try:
        response = requests.get(f"{STRATEGIES_URL}/strategies")
        strategies = response.json()  # pega o JSON
        return render_template('./strategies/list_strategies.html', strategies=strategies)
    except RequestException as e:
        return jsonify({"error": "Strategies service unavailable", "details": str(e)}), 503
    

@strategy_bp.route('/strategies/time/<int:strategy_id>', methods=['GET'])
def get_strategy_time(strategy_id):
    try:
        response = requests.get(f"{STRATEGIES_URL}/strategies/time/{strategy_id}")
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "Failed to get strategy time", "details": response.text}), response.status_code
    except RequestException as e:
        return jsonify({"error": "Strategies service unavailable", "details": str(e)}), 503