from flask import Blueprint, render_template, request, jsonify
from requests.exceptions import RequestException
import requests
from .services_routs import STRATEGIES_URL
from app import socketio
from flask_socketio import send


strategy_bp = Blueprint("strategy", __name__)

@strategy_bp.route('/strategies/create', methods=['POST', 'GET'])
def create_strategy():
    if request.method == 'POST':
        # Get the form data
        name = request.form.get("name")
        tatics = request.form.getlist("tatics")
        times = request.form.getlist("times")
        description = request.form.getlist("description")
        # return jsonify(name, tatics, times, description)

        # Junta tática + tempo
        tatics_with_times = [
            {"name": tatics[i], "time": float(times[i]), "description": description[i]}
            for i in range(len(tatics))
        ]

        # return f"{tatics_with_times}"

        # adicionando o chat_id para cada tática
        for tatics_with_time in tatics_with_times:
            if tatics_with_time["name"] == "Debate Sincrono":
                chat_requests = requests.post(f"{STRATEGIES_URL}/chat/create")
                
                if chat_requests.status_code == 200:
                    chat = chat_requests.json()
                    tatics_with_time["chat_id"] = chat["id"]
                else:
                    return jsonify({"error": "Failed to create chat", "details": chat_requests.text}), chat_requests.status_code
            else:
                tatics_with_time["chat_id"] = None
        
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
    
@strategy_bp.route('/chat/<int:strategy_id>', methods=['GET'])
def chat(strategy_id):
    # return 'oi'
    return render_template('/strategies/chat.html', strategy_id=strategy_id)


@strategy_bp.route('/chat/show', methods=['GET'])
def show_chats():
    mensagem_as_dic = requests.get(f"{STRATEGIES_URL}/chat/{id}").json()
    return jsonify(mensagem_as_dic), 200

@socketio.on('message')
def handle_message(data):
    id = data.get('id')
    username = data.get('username')
    content = data.get('content')

    mensagem = {
        "username": username,
        "content": content
    }

    mensagem_as_dic = requests.post(f"{STRATEGIES_URL}/chat/{id}/add_message", json=mensagem).json()

    
    # enviar para todos os clientes
    send(mensagem_as_dic, broadcast=True)

@socketio.on('load_messages')
def handle_load_messages(data):
    id = data.get('id')
    mensagem_as_dic = requests.get(f"{STRATEGIES_URL}/chat/{id}").json()
    send(mensagem_as_dic, broadcast=True)