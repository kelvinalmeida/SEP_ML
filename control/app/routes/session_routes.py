import logging
import sys
import json
import random
import string
import os
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from contextlib import contextmanager

# Assuming db.py is available in the python path (root of the service)
try:
    from db import create_connection
except ImportError:
    # If running from a different context where db is not top-level
    # This might need adjustment based on how the app is launched.
    # But based on user request "use db.py in control folder", and domain example.
    # We will try a relative import if this fails or assume it works.
    from ...db import create_connection

session_bp = Blueprint('session_bp', __name__)

def generate_unique_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Wrapper to use create_connection in a context manager style or just helper
@contextmanager
def get_db_connection():
    # create_connection takes db_url
    db_url = current_app.config.get("SQLALCHEMY_DATABASE_URI") or os.getenv("DATABASE_URL")
    conn = create_connection(db_url)
    if conn is None:
        raise Exception("Failed to connect to database")
    try:
        yield conn
    finally:
        conn.close()

def get_session_details(conn, session_id):
    with conn.cursor() as cur:
        # Get Session
        cur.execute("SELECT * FROM session WHERE id = %s", (session_id,))
        session = cur.fetchone()

        if not session:
            return None

        # Get Related Lists
        cur.execute("SELECT strategy_id FROM session_strategies WHERE session_id = %s", (session_id,))
        strategies = [row['strategy_id'] for row in cur.fetchall()]

        cur.execute("SELECT teacher_id FROM session_teachers WHERE session_id = %s", (session_id,))
        teachers = [row['teacher_id'] for row in cur.fetchall()]

        cur.execute("SELECT student_id FROM session_students WHERE session_id = %s", (session_id,))
        students = [row['student_id'] for row in cur.fetchall()]

        cur.execute("SELECT domain_id FROM session_domains WHERE session_id = %s", (session_id,))
        domains = [row['domain_id'] for row in cur.fetchall()]

        # Get VerifiedAnswers
        cur.execute("SELECT * FROM verified_answers WHERE session_id = %s", (session_id,))
        verified_answers = cur.fetchall()

        # Get ExtraNotes
        cur.execute("SELECT * FROM extra_notes WHERE session_id = %s", (session_id,))
        extra_notes = cur.fetchall()

        # Format the session dict to match the previous model.to_dict()
        session_dict = dict(session)
        # Ensure use_agent is present in the dict, defaulting to False if not in DB row (handled by SQL default)
        session_dict['use_agent'] = session.get('use_agent', False)
        session_dict['strategies'] = strategies
        session_dict['teachers'] = teachers
        session_dict['students'] = students
        session_dict['domains'] = domains
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

            cur.execute("""
                INSERT INTO session (status, code, current_tactic_index)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (
                'aguardando',
                code,
                0
            ))
            session_id = cur.fetchone()['id']

            # Insert relations
            if strategies:
                cur.executemany("INSERT INTO session_strategies (session_id, strategy_id) VALUES (%s, %s)",
                                [(session_id, str(s)) for s in strategies])
            if teachers:
                cur.executemany("INSERT INTO session_teachers (session_id, teacher_id) VALUES (%s, %s)",
                                [(session_id, str(t)) for t in teachers])
            if students:
                cur.executemany("INSERT INTO session_students (session_id, student_id) VALUES (%s, %s)",
                                [(session_id, str(s)) for s in students])
            if domains:
                cur.executemany("INSERT INTO session_domains (session_id, domain_id) VALUES (%s, %s)",
                                [(session_id, str(d)) for d in domains])

            conn.commit()

    return jsonify({"success": "Session created!"}), 200

@session_bp.route('/sessions', methods=['GET'])
def list_sessions():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM session")
            rows = cur.fetchall()

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

            # Cascading delete will handle related tables
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
    data = request.get_json() or {}
    use_agent = data.get('use_agent', False)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM session WHERE id = %s", (session_id,))
            if not cur.fetchone():
                return jsonify({"error": "Session not found"}), 404

            start_time = datetime.utcnow()
            cur.execute("""
                UPDATE session
                SET status = 'in-progress', start_time = %s, current_tactic_index = 0, current_tactic_started_at = %s, use_agent = %s
                WHERE id = %s
                RETURNING status, start_time
            """, (start_time, start_time, use_agent, session_id))
            updated = cur.fetchone()
            conn.commit()

    return jsonify({
        "session_id": session_id,
        "status": updated['status'],
        "start_time": updated['start_time'].isoformat(),
        "use_agent": use_agent
    })


@session_bp.route('/sessions/end/<int:session_id>', methods=['POST'])
def end_session(session_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, original_strategy_id FROM session WHERE id = %s", (session_id,))
            session = cur.fetchone()
            if not session:
                return jsonify({"error": "Session not found"}), 404

            # Revert to original strategy if it was changed
            if session['original_strategy_id']:
                original_strategy_id = session['original_strategy_id']
                # Revert session_strategies
                cur.execute("DELETE FROM session_strategies WHERE session_id = %s", (session_id,))
                cur.execute("INSERT INTO session_strategies (session_id, strategy_id) VALUES (%s, %s)",
                           (session_id, str(original_strategy_id)))

                # Clear the original_strategy_id column
                cur.execute("UPDATE session SET status = 'finished', original_strategy_id = NULL WHERE id = %s", (session_id,))
            else:
                cur.execute("UPDATE session SET status = 'finished' WHERE id = %s", (session_id,))

            conn.commit()

    return jsonify({"session_id": session_id, "message": "Session ended!"})


@session_bp.route('/sessions/<int:session_id>/temp_switch_strategy', methods=['POST'])
def temp_switch_strategy(session_id):
    data = request.get_json()
    new_strategy_id = data.get('strategy_id')

    if not new_strategy_id:
        return jsonify({"error": "Strategy ID is required"}), 400

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, original_strategy_id FROM session WHERE id = %s", (session_id,))
            session = cur.fetchone()
            if not session:
                return jsonify({"error": "Session not found"}), 404

            # If original_strategy_id is not set, it means we are on the original strategy.
            # We should save the current strategy before switching.
            if not session['original_strategy_id']:
                cur.execute("SELECT strategy_id FROM session_strategies WHERE session_id = %s", (session_id,))
                rows = cur.fetchall()
                # Assuming single strategy for now as per "change strategy" flow
                if rows:
                    current_strategy_id = rows[0]['strategy_id']
                    cur.execute("UPDATE session SET original_strategy_id = %s WHERE id = %s", (current_strategy_id, session_id))

            # Update to new strategy
            cur.execute("DELETE FROM session_strategies WHERE session_id = %s", (session_id,))
            cur.execute("INSERT INTO session_strategies (session_id, strategy_id) VALUES (%s, %s)", (session_id, str(new_strategy_id)))

            # Reset tactic index for the new strategy
            start_time = datetime.utcnow()
            cur.execute("""
                UPDATE session
                SET current_tactic_index = 0,
                    current_tactic_started_at = %s
                WHERE id = %s
            """, (start_time, session_id))

            conn.commit()

    return jsonify({"success": "Strategy temporarily switched!"}), 200


@session_bp.route('/sessions/tactic/next/<int:session_id>', methods=['POST'])
def next_tactic(session_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, current_tactic_index FROM session WHERE id = %s", (session_id,))
            session = cur.fetchone()
            if not session:
                return jsonify({"error": "Session not found"}), 404

            new_index = session['current_tactic_index'] + 1
            now = datetime.utcnow()

            cur.execute("""
                UPDATE session
                SET current_tactic_index = %s, current_tactic_started_at = %s
                WHERE id = %s
            """, (new_index, now, session_id))
            conn.commit()

    return jsonify({"success": True, "current_tactic_index": new_index})


@session_bp.route('/sessions/tactic/set/<int:session_id>', methods=['POST'])
def set_tactic_index(session_id):
    data = request.get_json()
    new_index = data.get('tactic_index')

    if new_index is None:
        return jsonify({"error": "tactic_index is required"}), 400

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM session WHERE id = %s", (session_id,))
            if not cur.fetchone():
                return jsonify({"error": "Session not found"}), 404

            now = datetime.utcnow()
            cur.execute("""
                UPDATE session
                SET current_tactic_index = %s, current_tactic_started_at = %s
                WHERE id = %s
            """, (new_index, now, session_id))
            conn.commit()

    return jsonify({"success": True, "current_tactic_index": new_index})


@session_bp.route('/sessions/tactic/prev/<int:session_id>', methods=['POST'])
def prev_tactic(session_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, current_tactic_index FROM session WHERE id = %s", (session_id,))
            session = cur.fetchone()
            if not session:
                return jsonify({"error": "Session not found"}), 404

            new_index = max(0, session['current_tactic_index'] - 1)
            now = datetime.utcnow()

            cur.execute("""
                UPDATE session
                SET current_tactic_index = %s, current_tactic_started_at = %s
                WHERE id = %s
            """, (new_index, now, session_id))
            conn.commit()

    return jsonify({"success": True, "current_tactic_index": new_index})


@session_bp.route('/sessions/submit_answer', methods=['POST'])
def submit_answer():
    data = request.get_json()
    student_id = str(data['student_id'])
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
    requester_id = str(data.get('requester_id')) # Ensure string for DB consistency
    user_type = data.get('type') # 'type' is a built-in function name

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM session WHERE code = %s", (session_code,))
            session = cur.fetchone()

            if not session:
                return jsonify({"error": "Session not found"}), 404

            session_id = session['id']

            # Check if already enrolled to avoid duplicates or error
            if user_type == 'student':
                cur.execute("SELECT 1 FROM session_students WHERE session_id = %s AND student_id = %s", (session_id, requester_id))
                if not cur.fetchone():
                    cur.execute("INSERT INTO session_students (session_id, student_id) VALUES (%s, %s)", (session_id, requester_id))
                    conn.commit()
            else:
                cur.execute("SELECT 1 FROM session_teachers WHERE session_id = %s AND teacher_id = %s", (session_id, requester_id))
                if not cur.fetchone():
                    cur.execute("INSERT INTO session_teachers (session_id, teacher_id) VALUES (%s, %s)", (session_id, requester_id))
                    conn.commit()

    return jsonify({"success": "Entered session successfully"}), 200

@session_bp.route('/sessions/<int:session_id>/change_strategy', methods=['POST'])
def change_session_strategy(session_id):
    data = request.get_json()
    new_strategy_id = data.get('strategy_id')

    if not new_strategy_id:
        return jsonify({"error": "Strategy ID is required"}), 400

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM session WHERE id = %s", (session_id,))
            if not cur.fetchone():
                return jsonify({"error": "Session not found"}), 404

            # Update strategy
            # First remove existing strategies (assuming single strategy replacement based on request description)
            # The schema allows multiple strategies (session_strategies table), but the prompt implies replacing "the" strategy.
            # I will clear all existing strategies for this session and add the new one.
            cur.execute("DELETE FROM session_strategies WHERE session_id = %s", (session_id,))
            cur.execute("INSERT INTO session_strategies (session_id, strategy_id) VALUES (%s, %s)", (session_id, str(new_strategy_id)))

            # Clear verified answers (full reset)
            cur.execute("DELETE FROM verified_answers WHERE session_id = %s", (session_id,))

            # Reset session state
            start_time = datetime.utcnow()
            cur.execute("""
                UPDATE session
                SET status = 'in-progress',
                    start_time = %s,
                    current_tactic_index = 0,
                    current_tactic_started_at = %s
                WHERE id = %s
            """, (start_time, start_time, session_id))

            conn.commit()

    return jsonify({"success": "Strategy changed and session restarted!"}), 200


@session_bp.route('/sessions/<int:session_id>/change_domain', methods=['POST'])
def change_session_domain(session_id):
    data = request.get_json()
    new_domain_id = data.get('domain_id')

    if not new_domain_id:
        return jsonify({"error": "Domain ID is required"}), 400

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM session WHERE id = %s", (session_id,))
            if not cur.fetchone():
                return jsonify({"error": "Session not found"}), 404

            # Update domain
            # Clear existing domains and add the new one
            cur.execute("DELETE FROM session_domains WHERE session_id = %s", (session_id,))
            cur.execute("INSERT INTO session_domains (session_id, domain_id) VALUES (%s, %s)", (session_id, str(new_domain_id)))

            # Clear verified answers (full reset)
            cur.execute("DELETE FROM verified_answers WHERE session_id = %s", (session_id,))

            # Reset session state
            start_time = datetime.utcnow()
            cur.execute("""
                UPDATE session
                SET status = 'in-progress',
                    start_time = %s,
                    current_tactic_index = 0,
                    current_tactic_started_at = %s
                WHERE id = %s
            """, (start_time, start_time, session_id))

            conn.commit()

    return jsonify({"success": "Domain changed and session restarted!"}), 200
