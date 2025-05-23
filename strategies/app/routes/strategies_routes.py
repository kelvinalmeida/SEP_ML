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