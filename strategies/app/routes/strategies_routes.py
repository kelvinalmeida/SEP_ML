from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import Strategies, Tatics, Message
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
    

@strategies_bp.route('/chat')
def chat():
    # return 'oi'
    return render_template('chat.html')

@strategies_bp.route('/chat/create', methods=['POST'])
def create_chat():    
    new_chat = Message()
    db.session.add(new_chat)
    db.session.commit()
    return jsonify({"success": "Chat created!", "id": new_chat.id}), 200

@strategies_bp.route('/chat/show', methods=['GET'])
def show_chats():
    all_chats = Message.query.all()
    return jsonify([{"id": c.id, "messages": c.messages} for c in all_chats]), 200

@strategies_bp.route('/chat/<int:chat_id>', methods=['GET'])
def get_chat(chat_id):
    chat = Message.query.get(chat_id)
    if chat:
        return jsonify(chat.as_dict()), 200
    return jsonify({"error": "Chat not found"}), 404

@strategies_bp.route('/chat/<int:chat_id>/add_message', methods=['POST'])
def add_message(chat_id):
    chat = Message.query.get(chat_id)
    if chat:
        username = request.json.get('username')
        content = request.json.get('content')
        chat.messages.append({"username": username, "content": content})
        db.session.commit()
        return jsonify(chat.as_dict()), 200
    return jsonify({"error": "Chat not found"}), 404


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
