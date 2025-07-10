from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import Session
from app import db
from datetime import datetime

session_bp = Blueprint('session_bp', __name__)

@session_bp.before_app_request
def create_tables():
    db.create_all()

@session_bp.route('/sessions/create', methods=['POST'])
def create_session():
    data = request.get_json()
    strategies = data.get('strategies', [])
    teachers = data.get('teachers', [])
    students = data.get('students', [])
    domains = data.get('domains', [])

    if not strategies:
        return jsonify({"error": "Strategies not provided"}), 400

    new_session = Session(
        status='aguardando',
        strategies=strategies,
        teachers=teachers,
        students=students,
        domains=domains,
    )

    db.session.add(new_session)
    db.session.commit()

    return jsonify({"success": "Session created!"}), 200



@session_bp.route('/sessions', methods=['GET'])
def list_sessions():
    all_sessions = Session.query.all()
    return jsonify([{"id": s.id, "status": s.status, "strategies": s.strategies, "teachers": s.teachers, "students": s.students, "domains": s.domains} for s in all_sessions])

@session_bp.route('/sessions/<int:session_id>', methods=['GET'])
def get_session_by_id(session_id):
    session = Session.query.get(session_id)
    if session:
        return jsonify({"id": session.id, "status": session.status, "strategies": session.strategies, "teachers": session.teachers, "students": session.students,  "domains": session.domains,  "start_time": session.start_time}), 200
    return jsonify({"error": "Session not found"}), 404
    

@session_bp.route('/sessions/delete/<int:session_id>', methods=['DELETE']) 
def delete_session(session_id):
    session = Session.query.get(session_id)
    if session:
        db.session.delete(session)
        db.session.commit()
        return jsonify({"success": "Session deleted!"}), 200
    return jsonify({"error": "Session not found"}), 404

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
        session.start_time = datetime.utcnow()
        db.session.commit()
        return jsonify({"session_id": session.id, "status": session.status, "start_time": session.start_time.isoformat()})
    return jsonify({"error": "Session not found"}), 404


@session_bp.route('/sessions/end/<int:session_id>', methods=['POST'])
def end_session(session_id):
    session = Session.query.get(session_id)
    if session:
        session.status = 'finished'
        db.session.commit()
        return jsonify({"session_id": session.id, "message": "Session ended!"})
    return jsonify({"error": "Session not found"}), 404


