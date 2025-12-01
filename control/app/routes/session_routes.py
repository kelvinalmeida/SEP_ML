import logging
import sys
import json
import random
import string
from flask import Blueprint, request, jsonify
from datetime import datetime
from app.db_client import get_db_connection

session_bp = Blueprint('session_bp', __name__)

def generate_unique_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_session_details(conn, session_id):
    with conn.cursor() as cur:
        # Get Session
        cur.execute("SELECT * FROM session WHERE id = %s", (session_id,))
        session = cur.fetchone()

        if not session:
            return None

        # Get VerifiedAnswers
        cur.execute("SELECT * FROM verified_answers WHERE session_id = %s", (session_id,))
        verified_answers = cur.fetchall()

        # Get ExtraNotes
        cur.execute("SELECT * FROM extra_notes WHERE session_id = %s", (session_id,))
        extra_notes = cur.fetchall()

        # Format the session dict to match the previous model.to_dict()
        session_dict = dict(session)
        session_dict['verified_answers'] = [dict(va) for va in verified_answers]
        session_dict['extra_notes'] = [dict(en) for en in extra_notes]

        return session_dict

@session_bp.route('/sessions/create', methods=['POST'])
def create_session():
    data = request.get_json()
    strategies = data.get('strategies', [])
    teachers = data.get('teachers', [])
    students = data.get('students', [])
    domains = data.get('domains', [])

    if not strategies:
        return jsonify({"error": "Strategies not provided"}), 400

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Generate unique code
            while True:
                code = generate_unique_code()
                cur.execute("SELECT 1 FROM session WHERE code = %s", (code,))
                if not cur.fetchone():
                    break

            # Insert session
            # Note: Postgres JSONB handles lists as JSON arrays.
            # We convert python lists to json strings/objects.
            # Psycopg2 adapts lists to arrays or json automatically depending on setup,
            # but explicit json.dumps is safer for JSONB columns if adapter isn't set.
            # However, with psycopg2.extras.Json or just passing the string.
            # Let's try passing the list directly and rely on psycopg2 or use json.dumps.
            # Using json.dumps ensures it goes in as JSON.

            cur.execute("""
                INSERT INTO session (status, strategies, teachers, students, domains, code)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                'aguardando',
                json.dumps(strategies),
                json.dumps(teachers),
                json.dumps(students),
                json.dumps(domains),
                code
            ))
            conn.commit()

    return jsonify({"success": "Session created!"}), 200

@session_bp.route('/sessions', methods=['GET'])
def list_sessions():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM session")
            rows = cur.fetchall()

            # This is N+1 but mimics previous behavior of calling to_dict() on all sessions
            # which fetched relations.
            # Optimization: could fetch all and join in memory, but sticking to logic.
            all_sessions = []
            for row in rows:
                details = get_session_details(conn, row['id'])
                if details:
                    all_sessions.append(details)

    return jsonify(all_sessions)

@session_bp.route('/sessions/<int:session_id>', methods=['GET'])
def get_session_by_id(session_id):
    with get_db_connection() as conn:
        session_dict = get_session_details(conn, session_id)

    if session_dict:
        return jsonify(session_dict), 200
        
    return jsonify({"error": "Session not found"}), 404
    

@session_bp.route('/sessions/delete/<int:session_id>', methods=['DELETE']) 
def delete_session(session_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM session WHERE id = %s", (session_id,))
            if not cur.fetchone():
                return jsonify({"error": "Session not found"}), 404

            # Cascading delete is handled by DB FKs (ON DELETE CASCADE)
            cur.execute("DELETE FROM session WHERE id = %s", (session_id,))
            conn.commit()

    return jsonify({"success": "Session deleted!"}), 200

@session_bp.route('/sessions/status/<int:session_id>', methods=['GET'])
def get_session_status(session_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, status FROM session WHERE id = %s", (session_id,))
            session = cur.fetchone()

    if session:
        return jsonify({"session_id": session['id'], "status": session['status']})
    return jsonify({"error": "Session not found"}), 404


@session_bp.route('/sessions/start/<int:session_id>', methods=['POST'])
def start_session(session_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM session WHERE id = %s", (session_id,))
            if not cur.fetchone():
                return jsonify({"error": "Session not found"}), 404

            start_time = datetime.utcnow()
            cur.execute("""
                UPDATE session
                SET status = 'in-progress', start_time = %s
                WHERE id = %s
                RETURNING status, start_time
            """, (start_time, session_id))
            updated = cur.fetchone()
            conn.commit()

    return jsonify({
        "session_id": session_id,
        "status": updated['status'],
        "start_time": updated['start_time'].isoformat()
    })


@session_bp.route('/sessions/end/<int:session_id>', methods=['POST'])
def end_session(session_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM session WHERE id = %s", (session_id,))
            if not cur.fetchone():
                return jsonify({"error": "Session not found"}), 404

            cur.execute("UPDATE session SET status = 'finished' WHERE id = %s", (session_id,))
            conn.commit()

    return jsonify({"session_id": session_id, "message": "Session ended!"})


@session_bp.route('/sessions/submit_answer', methods=['POST'])
def submit_answer():
    data = request.get_json()
    student_id = data['student_id']
    session_id = data['session_id']
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 1 FROM verified_answers
                WHERE student_id = %s AND session_id = %s
            """, (student_id, session_id))

            if cur.fetchone():
                return jsonify({"error": "Answer already submitted for this student"}), 409

            cur.execute("""
                INSERT INTO verified_answers (student_name, student_id, answers, score, session_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                data['student_name'],
                student_id,
                json.dumps(data['answers']),
                data.get('score', 0),
                session_id
            ))
            conn.commit()

    logging.basicConfig(level=logging.INFO)
    logging.info("🔍 dados das respostas no micr. control: %s", data)
    sys.stdout.flush()

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

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Check if exists
            cur.execute("""
                SELECT id FROM extra_notes
                WHERE estudante_username = %s AND session_id = %s
            """, (estudante_username, session_id))
            existing_note = cur.fetchone()

            if existing_note:
                cur.execute("""
                    UPDATE extra_notes
                    SET extra_notes = %s
                    WHERE id = %s
                """, (extra_notes, existing_note['id']))
                conn.commit()
                return jsonify({"message": "Extra notes updated successfully"}), 200

            cur.execute("""
                INSERT INTO extra_notes (estudante_username, student_id, extra_notes, session_id)
                VALUES (%s, %s, %s, %s)
            """, (estudante_username, student_id, extra_notes, session_id))
            conn.commit()

            # Logging new note info for consistency with previous code
            logging.info("🔍 new_note inserted for student_id: %s", student_id)
            sys.stdout.flush()

    return jsonify({"message": "Extra notes added successfully"}), 201


@session_bp.route('/sessions/enter', methods=['POST'])
def enter_session():
    data = request.get_json()

    session_code = data.get('session_code')
    requester_id = data.get('requester_id')
    user_type = data.get('type') # 'type' is a built-in function name

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, students, teachers FROM session WHERE code = %s", (session_code,))
            session = cur.fetchone()

            if not session:
                return jsonify({"error": "Session not found"}), 404

            session_id = session['id']
            # Postgres returns JSONB as list/dict if using RealDictCursor and appropriate driver setting,
            # or we might need to load it.
            # Psycopg2 with RealDictCursor usually returns the python object for JSON types.
            students = session['students']
            teachers = session['teachers']

            # Ensure they are lists (in case they are None or string?)
            if isinstance(students, str):
                students = json.loads(students)
            if isinstance(teachers, str):
                teachers = json.loads(teachers)

            if students is None: students = []
            if teachers is None: teachers = []

            updated = False
            if user_type == 'student':
                if requester_id not in students:
                    students.append(requester_id)
                    updated = True
                    cur.execute("UPDATE session SET students = %s WHERE id = %s", (json.dumps(students), session_id))
            else:
                if requester_id not in teachers:
                    teachers.append(requester_id)
                    updated = True
                    cur.execute("UPDATE session SET teachers = %s WHERE id = %s", (json.dumps(teachers), session_id))

            if updated:
                conn.commit()

    return jsonify({"success": "Entered session successfully"}), 200
