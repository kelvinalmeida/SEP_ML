from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import Strategies
from app import db



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

    new_strategy = Strategies(name=name, tatics=tatics)
    db.session.add(new_strategy)
    db.session.commit()
    return jsonify({"success": "Strategie created!"}), 200


@strategies_bp.route('/strategies', methods=['GET'])
def list_strategies():
    all_strategies = Strategies.query.all()
    return jsonify([{"id": s.id, "name": s.name, "tatics": s.tatics} for s in all_strategies]), 200

# @strategies_bp.route('/strategies/status/<int:session_id>', methods=['GET'])
# def get_session_status(session_id):
#     session = Session.query.get(session_id)
#     if session:
#         return jsonify({"session_id": session.id, "status": session.status})
#     return jsonify({"error": "Session not found"}), 404

# @strategies_bp.route('/strategies/start/<int:session_id>', methods=['POST'])
# def start_session(session_id):
#     session = Session.query.get(session_id)
#     if session:
#         session.status = 'in-progress'
#         db.session.commit()
#         return jsonify({"session_id": session.id, "status": session.status})
#     return jsonify({"error": "Session not found"}), 404

# @strategies_bp.route('/strategies/end/<int:session_id>', methods=['POST'])
# def end_session(session_id):
#     session = Session.query.get(session_id)
#     if session:
#         session.status = 'finished'
#         db.session.commit()
#         return jsonify({"session_id": session.id, "message": "Session ended!"})
#     return jsonify({"error": "Session not found"}), 404
