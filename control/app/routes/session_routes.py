from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import Session
from app import db

session_bp = Blueprint('session_bp', __name__)

@session_bp.before_app_request
def create_tables():
    db.create_all()

@session_bp.route('/sessions/create', methods=['GET', 'POST'])
def create_session():
    if request.method == 'POST':
        strategy = request.form['strategy']
        new_session = Session(status='aguardando', strategy=strategy)
        db.session.add(new_session)
        db.session.commit()
        return redirect(url_for('session_bp.success'))
    return render_template('create_session.html')

@session_bp.route('/success')
def success():
    return 'Sessão criada com sucesso!'

@session_bp.route('/sessions', methods=['GET'])
def list_sessions():
    all_sessions = Session.query.all()
    return render_template('list_sessions.html', sessions=all_sessions)

@session_bp.route('/sessions/status/<int:session_id>', methods=['GET'])
def get_session_status(session_id):
    session = Session.query.get(session_id)
    if session:
        return jsonify({"session_id": session.id, "status": session.status})
    return jsonify({"error": "Session not found"}), 404

@session_bp.route('/sessions/start/<int:session_id>', methods=['POST'])
def start_session(session_id):
    session = Session.query.get(session_id)
    if session:
        session.status = 'in-progress'
        db.session.commit()
        return jsonify({"session_id": session.id, "status": session.status})
    return jsonify({"error": "Session not found"}), 404

@session_bp.route('/sessions/end/<int:session_id>', methods=['POST'])
def end_session(session_id):
    session = Session.query.get(session_id)
    if session:
        session.status = 'finished'
        db.session.commit()
        return jsonify({"session_id": session.id, "message": "Session ended!"})
    return jsonify({"error": "Session not found"}), 404
