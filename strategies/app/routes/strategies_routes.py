from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import Strategies, Tatics, Message
from app import db, socketio  # importar o socketio criado no __init__.py
from flask_socketio import send



strategies_bp = Blueprint('strategies_bp', __name__)

@strategies_bp.before_app_request
def create_tables():
    db.create_all()

@strategies_bp.route('/strategies/create', methods=['POST', 'GET'])
def create_strategy():
    # Assuming you have a model named Strategies with the following fields:
    # id = db.Column(db.Integer, primary_key=True)
    # name = db.Column(db.String(50), nullable=False)
    # students = db.Column(PickleType, nullable=False, default=[])
    # teachers = db.Column(PickleType, nullable=False, default=[])
    # tatics = db.Column(PickleType, nullable=False, default=[])
    

    name = request.json.get('name')
    tatics = request.json.get('tatics')

    tatatics = [ Tatics(description=tatic["description"], name=tatic["name"], time=tatic["time"]) for tatic in tatics]


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
    # Assuming you have a model named Message with the following fields:
    # id = db.Column(db.Integer, primary_key=True)
    # messages = db.Column(PickleType, nullable=False, default=[])
    
    new_chat = Message()
    db.session.add(new_chat)
    db.session.commit()
    return jsonify({"success": "Chat created!", "id": new_chat.id}), 200

@strategies_bp.route('/chat/show', methods=['GET'])
def show_chats():
    all_chats = Message.query.all()
    return jsonify([{"id": c.id, "messages": c.messages} for c in all_chats]), 200

@socketio.on('message')
def handle_message(data):
    id = data.get('id')
    username = data.get('username')
    content = data.get('content')

    chat = Message.query.filter_by(id=id).first()

    # print(f'>>>>>>>>>>>>>> {chat.messages}')
    chat.messages.append({"username": username, "content": content})
    db.session.commit()

    # enviar para todos os clientes
    send(chat.as_dict(), broadcast=True)

@socketio.on('load_messages')
def handle_load_messages():
    chat = Message.query.filter_by(id=1).first()
    send(chat.as_dict(), broadcast=True)