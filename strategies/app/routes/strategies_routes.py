from operator import or_
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import Strategies, Tatics, Message, PrivateMessage
from app import db  # importar o socketio criado no __init__.py



strategies_bp = Blueprint('strategies_bp', __name__)

@strategies_bp.before_app_request
def create_tables():
    db.create_all()

@strategies_bp.route('/strategies/create', methods=['POST', 'GET'])
def create_strategy():

    name = request.json.get('name')
    tatics = request.json.get('tatics')

    tatatics = [ Tatics(description=tatic["description"], name=tatic["name"], time=tatic["time"], chat_id=tatic["chat_id"]) for tatic in tatics]


    new_strategy = Strategies(name=name, tatics=tatatics)
    db.session.add(new_strategy)
    db.session.commit()
    return jsonify({"success": "Strategie created!"}), 200


@strategies_bp.route('/strategies', methods=['GET'])
def list_strategies():
    all_strategies = Strategies.query.all()
    return jsonify([{"id": s.id, "name": s.name, "tatics": [t.as_dict() for t in s.tatics]} for s in all_strategies]), 200


@strategies_bp.route('/strategies/<int:strategy_id>', methods=['GET'])
def strategy_by_id(strategy_id):
    strategy = Strategies.query.get(strategy_id)
    if strategy:
        return jsonify({"id": strategy.id, "name": strategy.name, "tatics": [t.as_dict() for t in strategy.tatics]}), 200
    return jsonify({"error": "Strategy not found"}), 404


@strategies_bp.route('/strategies/time/<int:strategy_id>', methods=['GET'])
def get_strategy_by_id(strategy_id):
    strategy = Strategies.query.get(strategy_id)
    if strategy:
        return jsonify({"id": strategy.id, "name": strategy.name, "tatics": [t.as_dict() for t in strategy.tatics]}), 200
    return jsonify({"error": "Strategy not found"}), 404


@strategies_bp.route('/strategies/full_tatics_time', methods=['GET'])
def get_full_tatics_time():
    ids = request.args.getlist('ids')
    
    if not ids:
        return jsonify({"error": "No IDs provided"}), 400

    try:
        # converte todos os ids para inteiros
        ids = list(map(int, ids))
    except ValueError:
        return jsonify({"error": "IDs must be integers"}), 400

    strategies = Strategies.query.filter(Strategies.id.in_(ids)).all()

    if not strategies:
        return jsonify({"error": "No strategies found"}), 404

    full_tactics_time = 0

    for strategy in strategies:
        for tactic in strategy.tatics:  # Acesso via atributo, não via dicionário
            full_tactics_time += getattr(tactic, "time", 0)  # ou tactic.time se tiver certeza que tem esse atributo

    return jsonify({"full_tactics_time": full_tactics_time}), 200

@strategies_bp.route('/strategies/remove/<int:strategy_id>', methods=['DELETE'])
def remove_strategy(strategy_id):
    strategy = Strategies.query.get(strategy_id)
    if not strategy:
        return jsonify({"error": "Strategy not found"}), 404
    
    db.session.delete(strategy)
    db.session.commit()
    return jsonify({"success": "Strategy removed!"}), 200
    

@strategies_bp.route('/chat')
def chat():
    # return 'oi'
    return render_template('chat.html')

@strategies_bp.route('/chat/show', methods=['GET'])
def show_chats():
    all_chats = Message.query.all()
    return jsonify([{"id": c.id, "messages": c.messages} for c in all_chats]), 200

# Criar uma nova mensagem privada
@strategies_bp.route('/private_chat/send', methods=['POST'])
def send_private_message():
    data = request.json
    msg = PrivateMessage(
        sender_id=data['sender_id'],
        receiver_id=data['receiver_id'],
        content=data['content']
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify(msg.as_dict()), 201


@strategies_bp.route('/strategies/ids_to_names', methods=['GET'])
def ids_to_names():
    ids = request.args.getlist('ids')
    
    if not ids:
        return jsonify({"error": "No IDs provided"}), 400

    try:
        # converte todos os ids para inteiros
        ids = list(map(int, ids))
    except ValueError:
        return jsonify({"error": "IDs must be integers"}), 400

    strategies = Strategies.query.filter(Strategies.id.in_(ids)).all()

    if not strategies:
        return jsonify({"error": "No strategies found"}), 404

    result = [ {
        "name": strategy.name, 
        "tatics": [tatic.as_dict() for tatic in strategy.tatics] } 
        for strategy in strategies ]

    return jsonify(result), 200


@strategies_bp.route('/chat/<int:strategy_id>', methods=['GET'])
def get_strategy_chat(strategy_id):
    chat = Message.query.get(strategy_id)
    if chat:
        return jsonify(chat.as_dict()), 200
    return jsonify({"error": "Chat not found"}), 404


@strategies_bp.route('/chat/create', methods=['POST'])
def create_chat():    
    new_chat = Message()
    db.session.add(new_chat)
    db.session.commit()
    return jsonify({"success": "Chat created!", "id": new_chat.id}), 200


# --- NOVOS ENDPOINTS ---

@strategies_bp.route('/chat/<int:chat_id>/general_messages', methods=['GET'])
def get_general_messages(chat_id):
    """Retorna apenas as mensagens do chat geral."""
    chat = Message.query.get(chat_id)
    if chat:
        return jsonify(chat.as_dict()), 200 
    return jsonify({"error": "Chat not found"}), 404

@strategies_bp.route('/chat/<int:chat_id>/private_messages/<string:myUsername>/<string:target_username>', methods=['GET'])
def get_private_messages(chat_id, myUsername, target_username):
    """Retorna o histórico de mensagens entre dois usuários específicos."""
    chat = Message.query.get(chat_id)
    if not chat:
        return jsonify({"error": "Chat not found"}), 404
        
    messages = PrivateMessage.query.filter(
        PrivateMessage.message_id == chat_id,
        or_(
            (PrivateMessage.username == myUsername) & (PrivateMessage.target_username == target_username),
            (PrivateMessage.username == target_username) & (PrivateMessage.target_username == myUsername)
        )
    ).order_by(PrivateMessage.timestamp.asc()).all()
    
    return jsonify([msg.as_dict() for msg in messages]), 200

@strategies_bp.route('/chat/<int:chat_id>/add_message', methods=['POST'])
def add_message(chat_id):
    """Adiciona uma mensagem ao chat geral. Retorna apenas a mensagem adicionada."""
    chat = Message.query.get(chat_id)
    if not chat:
        return jsonify({"error": "Chat not found"}), 404
    
    data = request.json
    new_message = {"username": data.get('username'), "content": data.get('content')}
    chat.messages.append(new_message)
    db.session.commit()
    return jsonify(new_message), 201 # 201 Created

@strategies_bp.route('/chat/<int:chat_id>/add_priv_message', methods=['POST'])
def add_priv_message(chat_id):
    """Adiciona uma mensagem privada. Retorna a mensagem criada."""
    chat = Message.query.get(chat_id)
    if not chat:
        return jsonify({"error": "Chat not found"}), 404

    data = request.json
    msg = PrivateMessage(
        sender_id=data.get('sender_id'),
        content=data.get('content'),
        username=data.get('username'), # Adicionando username
        target_username=data.get('target_username') # Adicionando target_username
    )
    chat.messages_privates.append(msg)
    # Não precisa de db.session.add(msg) por causa do cascade
    db.session.commit()
    
    return jsonify(msg.as_dict()), 201


