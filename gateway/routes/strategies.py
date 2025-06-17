from flask import Blueprint, render_template, request, jsonify, session
from requests.exceptions import RequestException
import requests
from .services_routs import STRATEGIES_URL, CONTROL_URL, USER_URL
from app import socketio
from flask_socketio import join_room, leave_room, send, emit
from .auth import token_required
import json


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
    
# gateway.py

# import json
# import requests
# from requests.exceptions import RequestException
# from flask import render_template, jsonify, session
# from flask_socketio import join_room, leave_room, send, emit
# from . import strategy_bp  # ou sua importação de blueprint
# from your_app import socketio  # Importe sua instância do socketio

# # URLs das suas APIs
# CONTROL_URL = "http://localhost:5001"
# USER_URL = "http://localhost:5002"
# STRATEGIES_URL = "http://localhost:5003" # URL da sua API de Estratégias

# --- ROTA HTTP ---
# Esta rota agora apenas prepara o ambiente do chat.

# @strategy_bp.route('/chat/<int:chat_id>', methods=['GET'])
# def chat_(chat_id):
#     # return f'${chat_id}'
#     return render_template('/strategies/chat.html', chat_id=chat_id)

@strategy_bp.route('/chat/<int:chat_id>/<int:session_id>', methods=['GET'])
@token_required
def chat(chat_id, session_id, current_user=None):
    try:
        # A lógica para buscar usuários permanece a mesma
        response = requests.get(f"{CONTROL_URL}/sessions/{session_id}")
        response.raise_for_status()
        
        session_data = response.json()
        students = session_data.get("students", [])
        teachers = session_data.get("teachers", [])
        
        
        # Uma única chamada para buscar todos os nomes de uma vez é mais eficiente
        teachers = {'ids': teachers}
        students = {'ids': students}
        students_response = requests.get(f"{USER_URL}/students/ids_to_names", params=students)
        students_response.raise_for_status()
        teachers_response = requests.get(f"{USER_URL}/teachers/ids_to_names", params=teachers)
        teachers_response.raise_for_status()
        # return f"{users_response.json()}"

        all_user_names = list(set(students_response.json()['names'] + teachers_response.json()['names']))

        # Guarda o ID do usuário na sessão do Flask para uso nos sockets
        
        session['user_id'] = current_user['id']
        session['username'] = current_user['name']

        all_users = json.dumps(all_user_names)

        # return f"{chat_id}, {all_users}"
        
        # Passa a lista de usuários e o usuário atual para o template
        return render_template(
            '/strategies/chat.html', 
            chat_id=chat_id, 
            current_user=current_user, 
            all_users=all_users # Passa uma lista simples de usuários
        )
    except RequestException as e:
        return jsonify({"error": "Service unavailable", "details": str(e)}), 503

# --- EVENTOS SOCKET.IO ---

@socketio.on('connect')
def handle_connect():
    # O cliente enviará um evento 'join' após conectar
    print("Cliente conectado")

@socketio.on('join')
def on_join(data):
    """Cliente entra em uma sala específica para este chat."""
    username = session.get('username')
    chat_id = data['chat_id']
    
    # Adiciona o cliente à sala do chat
    join_room(chat_id)
    print(f'Usuário {username} entrou na sala {chat_id}')
    
    
@socketio.on('disconnect')
def on_disconnect():
    """Cliente se desconecta e sai da sala."""
    username = session.get('username')
    # O Flask-SocketIO remove o cliente das salas automaticamente,
    # mas podemos notificar os outros se tivermos o chat_id.
    print(f'Usuário {username} desconectou.')

@socketio.on('load_general_messages')
def handle_load_general(data):
    """Busca o histórico de mensagens gerais na API."""
    chat_id = data.get('chat_id')
    try:
        response = requests.get(f"{STRATEGIES_URL}/chat/{chat_id}/general_messages")
        response.raise_for_status()
        emit('general_messages_history', response.json())
    except RequestException as e:
        emit('error', {"details": f"Não foi possível carregar o histórico geral: {str(e)}"})

@socketio.on('load_private_messages')
def handle_load_private(data):
    """Busca o histórico de mensagens privadas entre dois usuários."""
    chat_id = data.get('chat_id')
    user1_id = session.get('user_id')
    user2_id = data.get('with_user_id')
    try:
        response = requests.get(f"{STRATEGIES_URL}/chat/{chat_id}/private_messages/{user1_id}/{user2_id}")
        response.raise_for_status()
        # Envia o histórico de volta para o cliente que pediu
        emit('private_messages_history', {'with_user_id': user2_id, 'messages': response.json()})
    except RequestException as e:
        emit('error', {"details": f"Não foi possível carregar o histórico privado: {str(e)}"})
        
@socketio.on('general_message')
def handle_general_message(data):
    """Recebe uma mensagem geral, salva via API e retransmite para a sala."""
    chat_id = data.get('chat_id')
    message_payload = {
        "username": session.get('username'),
        "content": data.get('content')
    }
    try:
        # Salva a mensagem na API
        requests.post(f"{STRATEGIES_URL}/chat/{chat_id}/add_message", json=message_payload)
        # Retransmite para todos na sala
        emit('new_general_message', message_payload, to=chat_id)
    except RequestException as e:
        emit('error', {"details": f"Não foi possível enviar a mensagem: {str(e)}"})

@socketio.on('private_message')
def handle_private_message(data):
    """Recebe uma mensagem privada, salva e a envia para o destinatário correto."""
    chat_id = data.get('chat_id')
    sender_id = session.get('user_id')
    recipient_id = data.get('recipient_id')

    message_payload = {
        "sender_id": sender_id,
        "receiver_id": int(recipient_id), # Garante que é int
        "content": data.get('content'),
        "username": session.get('username') # Incluindo o nome de quem envia
    }
    try:
        # Salva a mensagem privada na API
        response = requests.post(f"{STRATEGIES_URL}/chat/{chat_id}/add_priv_message", json=message_payload)
        new_message = response.json() # A API deve retornar a mensagem criada

        # A lógica para enviar ao destinatário específico é complexa sem um mapeamento user->socket.
        # A abordagem mais simples com rooms é enviar para a sala geral e o cliente decide se exibe.
        # O ideal seria ter uma sala por conversa privada (ex: join_room(f'private_{sender_id}_{recipient_id}'))
        emit('new_private_message', new_message, to=chat_id)
        
    except RequestException as e:
        emit('error', {"details": f"Não foi possível enviar a mensagem privada: {str(e)}"})