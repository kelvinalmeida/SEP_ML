import logging
import sys
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import Session, VerifiedAnswers, ExtraNotes
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
    return jsonify([s.to_dict() for s in all_sessions])
    # return jsonify([{"id": s.id, "status": s.status, "strategies": s.strategies, "teachers": s.teachers, "students": s.students, "domains": s.domains} for s in all_sessions])

@session_bp.route('/sessions/<int:session_id>', methods=['GET'])
def get_session_by_id(session_id):
    session = Session.query.get(session_id)
    if session:
        return jsonify(session.to_dict()), 200
        # return jsonify({"id": session.id, "status": session.status, "strategies": session.strategies, "teachers": session.teachers, "students": session.students,  "domains": session.domains,  "start_time": session.start_time}), 200
        
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


@session_bp.route('/sessions/submit_answer', methods=['POST'])
def submit_answer():
    data = request.get_json()
    
    verified_answers = VerifiedAnswers.query.filter_by(student_id=data['student_id'], session_id=data['session_id']).first()

    if verified_answers:
        return jsonify({"error": "Answer already submitted for this student"}), 409

    new_verified_answer = VerifiedAnswers(
        student_name=data['student_name'],
        student_id=data['student_id'],
        answers=data['answers'],
        score=data.get('score', 0),  # Use the score from the data or default to 0
        session_id=data['session_id']
    )

    db.session.add(new_verified_answer)
    db.session.commit()

    logging.basicConfig(level=logging.INFO)
    logging.info("🔍 dados das respostas no micr. control: %s", data)
    sys.stdout.flush()

    # Aqui você pode validar ou simular algo com os dados
    # Por enquanto apenas retorna os dados recebidos
    return jsonify(data), 200


@session_bp.route("/sessions/add_extra_notes", methods=["POST"])
def add_extra_notes():

    logging.basicConfig(level=logging.INFO)
    logging.info("oiiiiiii")
    sys.stdout.flush()

    data = request.json

    extra_notes = float(data.get("extra_notes", 0.0))
    session_id = int(data.get("session_id"))
    student_id = int(data.get("student_id", 0))
    estudante_username = data.get("estudante_username", "")

    

    estudent_extra_notes = ExtraNotes.query.filter_by(estudante_username=estudante_username, session_id=session_id).first()
    
    if estudent_extra_notes:
        estudent_extra_notes.extra_notes = extra_notes
        db.session.commit()
        return jsonify({"message": "Extra notes updated successfully"}), 200

    new_note = ExtraNotes(
        estudante_username=data.get("estudante_username", ""),
        student_id=student_id,
        extra_notes=extra_notes,
        session_id=session_id
    )

    logging.basicConfig(level=logging.INFO)
    logging.info("🔍 new_note: %s", new_note)
    sys.stdout.flush()


    db.session.add(new_note)
    db.session.commit()

    return jsonify({"message": "Extra notes added successfully"}), 201


@session_bp.route('/sessions/enter', methods=['POST'])
def enter_session():
    data = request.get_json()

    session_code = data.get('session_code')
    requester_id = data.get('requester_id')
    type = data.get('type')

    session = Session.query.filter_by(code=session_code).first()

    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    if type == 'student':
        if requester_id not in session.students:
            session.students.append(requester_id)
            db.session.commit()
    else:
        if requester_id not in session.teachers:
            session.teachers.append(requester_id)
            db.session.commit()


    db.session.refresh(session)

    return jsonify({"success": "Entered session successfully"}), 200

