from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from requests.exceptions import RequestException
import requests
from .auth import token_required
from .services_routs import CONTROL_URL, STRATEGIES_URL, USER_URL

session_bp = Blueprint("session", __name__)


@session_bp.route('/sessions/create', methods=['GET', "POST"])
@token_required
def create_session(current_user=None):
    if request.method == 'POST':
        try:
            strategy_ids = request.form.getlist('strategies')  # agora é uma lista
            teacher_ids = request.form.getlist('teachers')
            student_ids = request.form.getlist('students')

            data = {
                "strategies": strategy_ids,
                "teachers": teacher_ids,
                "students": student_ids
            }

            response = requests.post(f"{CONTROL_URL}/sessions/create", json=data)

            if response.status_code == 200:
                return redirect(url_for('session_bp.home_page'))  # ou qualquer outra página
            else:
                return f"Erro ao criar sessão: {response.status_code}", response.status_code
        except RequestException as e:
            return jsonify({"error": "Control service unavailable", "details": str(e)}), 503
    else:
        strategies = requests.get(f"{STRATEGIES_URL}/strategies").json()
        teachers = requests.get(f"{USER_URL}/teachers").json()
        students = requests.get(f"{USER_URL}/students").json()

        return render_template("control/create_session.html", strategies=strategies, teachers=teachers, students=students)


@session_bp.route('/sessions', methods=['GET'])
@token_required
def list_sessions(current_user=None):
    try:
        # Busca todas as sessões no microserviço control
        response = requests.get(f"{CONTROL_URL}/sessions")
        if response.status_code != 200:
            return f"Erro ao buscar sessões: {response.status_code}", response.status_code

        sessions = response.json()

        # return sessions

        # Busca nomes de estratégias, professores e estudantes
        strategies_data = requests.get(f"{STRATEGIES_URL}/strategies").json()
        teachers_data = requests.get(f"{USER_URL}/teachers").json()
        students_data = requests.get(f"{USER_URL}/students").json()

        # Cria dicionários para mapear IDs para nomes
        strategy_map = {str(item["id"]): item["name"] for item in strategies_data}
        teacher_map = {str(item["id"]): item["name"] for item in teachers_data}
        student_map = {str(item["id"]): item["name"] for item in students_data}

        # Substitui os IDs por nomes nas sessões
        for session in sessions:
            session["strategies"] = [strategy_map.get(str(sid), f"ID {sid}") for sid in session.get("strategies", [])]
            session["teachers"] = [teacher_map.get(str(tid), f"ID {tid}") for tid in session.get("teachers", [])]
            session["students"] = [student_map.get(str(sid), f"ID {sid}") for sid in session.get("students", [])]


        return render_template("control/list_all_sessions.html", sessions=sessions)

    except RequestException as e:
        return jsonify({"error": "Service unavailable", "details": str(e)}), 503


@session_bp.route('/sessions/<int:session_id>', methods=['GET'])
@token_required
def get_session_by_id(session_id, current_user=None):
    try:
        # Busca todas as sessões no microserviço control
        response = requests.get(f"{CONTROL_URL}/sessions/{session_id}")

        if response.status_code != 200:
            return f"Erro ao buscar sessões: {response.status_code}", response.status_code

        session = response.json()

        # Busca nomes de estratégias, professores e estudantes
        strategies_data = requests.get(f"{STRATEGIES_URL}/strategies").json()
        teachers_data = requests.get(f"{USER_URL}/teachers").json()
        students_data = requests.get(f"{USER_URL}/students").json()

        # Cria dicionários para mapear IDs para nomes
        strategy_map = {str(item["id"]): item["name"] for item in strategies_data}
        teacher_map = {str(item["id"]): item["name"] for item in teachers_data}
        student_map = {str(item["id"]): item["name"] for item in students_data}

        # Substitui os IDs por nomes nas sessões

        session["strategies"] = [strategy_map.get(str(sid), f"ID {sid}") for sid in session.get("strategies", [])]
        session["teachers"] = [teacher_map.get(str(tid), f"ID {tid}") for tid in session.get("teachers", [])]
        session["students"] = [student_map.get(str(sid), f"ID {sid}") for sid in session.get("students", [])]

        # return 'ou'
        return render_template("control/show_session.html", session=session)

    except RequestException as e:
        return jsonify({"error": "Service unavailable", "details": str(e)}), 503

@session_bp.route('/sessions/status/<int:session_id>', methods=['GET'])
@token_required
def get_session_status(session_id, current_user=None):
    try:
        response = requests.get(f"{CONTROL_URL}/sessions/status/{session_id}")
        return (response.text, response.status_code, response.headers.items())
    except RequestException as e:
        return jsonify({"error": "Control service unavailable", "details": str(e)}), 503


@session_bp.route('/sessions/start/<int:session_id>', methods=['POST'])
@token_required
def start_session(session_id, current_user=None):
    try:
        response = requests.post(f"{CONTROL_URL}/sessions/start/{session_id}")
        return (response.text, response.status_code, response.headers.items())
    except RequestException as e:
        return jsonify({"error": "Control service unavailable", "details": str(e)}), 503


@session_bp.route('/sessions/end/<int:session_id>', methods=['POST'])
@token_required
def end_session(session_id, current_user=None):
    try:
        response = requests.post(f"{CONTROL_URL}/sessions/end/{session_id}")
        return (response.text, response.status_code, response.headers.items())
    except RequestException as e:
        return jsonify({"error": "Control service unavailable", "details": str(e)}), 503
