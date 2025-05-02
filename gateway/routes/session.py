from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from requests.exceptions import RequestException
import requests
from .auth import token_required
from datetime import datetime
from .services_routs import CONTROL_URL, STRATEGIES_URL, USER_URL, DOMAIN_URL

session_bp = Blueprint("session", __name__)


@session_bp.route('/sessions/create', methods=['GET', "POST"])
@token_required
def create_session(current_user=None):
    if request.method == 'POST':
        try:
            strategy_ids = request.form.getlist('strategies')  # agora é uma lista
            teacher_ids = request.form.getlist('teachers')
            student_ids = request.form.getlist('students')
            domains_ids = request.form.getlist('domains')

            data = {
                "strategies": strategy_ids,
                "teachers": teacher_ids,
                "students": student_ids,
                "domains": domains_ids,
            }

            response = requests.post(f"{CONTROL_URL}/sessions/create", json=data)

            if response.status_code == 200:
                return redirect(url_for('login.home_page'))  # ou qualquer outra página
            else:
                return f"Erro ao criar sessão: {response.status_code}", response.status_code
        except RequestException as e:
            return jsonify({"error": "Control service unavailable", "details": str(e)}), 503
    else:
        strategies = requests.get(f"{STRATEGIES_URL}/strategies").json()
        teachers = requests.get(f"{USER_URL}/teachers").json()
        students = requests.get(f"{USER_URL}/students").json()
        domains = requests.get(f"{DOMAIN_URL}/domains").json()
        # return f"{domains}"

        return render_template("control/create_session.html", strategies=strategies, teachers=teachers, students=students, domains=domains)


@session_bp.route('/sessions', methods=['GET'])
@token_required
def list_sessions(current_user=None):
    # return current_user
    try:
        # Busca todas as sessões
        response = requests.get(f"{CONTROL_URL}/sessions")
        if response.status_code != 200:
            return f"Erro ao buscar sessões: {response.status_code}", response.status_code

        sessions = response.json()
        # return f"{sessions}"

        # Buscar apenas os nomes das estratégias, professores e alunos
        strategy_data = requests.get(f"{STRATEGIES_URL}/strategies").json()
        teacher_data = requests.get(f"{USER_URL}/teachers").json()
        student_data = requests.get(f"{USER_URL}/students").json()
        domains_data = requests.get(f"{DOMAIN_URL}/domains").json()

        # Mapear apenas os nomes por ID
        strategy_map = {str(item["id"]): item["name"] for item in strategy_data}
        teacher_map = {str(item["id"]): item["name"] for item in teacher_data}
        student_map = {str(item["id"]): item["name"] for item in student_data}
        domains_map = {str(item["id"]): item["name"] for item in domains_data}
        
        # return f"{domains_map}"
        # return f"{domains_map.get(sessions[0].get('domains', [])[0])}"

        for session in sessions:
            session["strategies"] = [
                strategy_map.get(str(sid), f"ID {sid}")
                for sid in session.get("strategies", [])
            ]
            session["teachers"] = [
                teacher_map.get(str(tid), f"ID {tid}")
                for tid in session.get("teachers", [])
            ]
            session["students"] = [
                student_map.get(str(sid), f"ID {sid}")
                for sid in session.get("students", [])
            ]
            session["domains"] = [
                domains_map.get(str(sid), f"ID {sid}")
                for sid in session.get("domains", [])
            ]
        
        return render_template("control/list_all_sessions.html", sessions=sessions, current_user=current_user)

    except RequestException as e:
        return jsonify({"error": "Service unavailable", "details": str(e)}), 503




@session_bp.route('/sessions/<int:session_id>', methods=['GET', 'POST'])
@token_required
def get_session_by_id(session_id, current_user=None):

    if request.method == 'POST':
        response = requests.delete(f"{CONTROL_URL}/sessions/start/{session_id}")
        return (response.text, response.status_code, response.headers.items())

    try:
        # Busca sessão específica no microserviço control
        response = requests.get(f"{CONTROL_URL}/sessions/{session_id}")
        if response.status_code != 200:
            return f"Erro ao buscar sessão: {response.status_code}", response.status_code

        session = response.json()

        # return f"{session}"

        # Busca estratégias com táticas
        strategies_data = requests.get(f"{STRATEGIES_URL}/strategies").json()

        # Cria dicionário de estratégias por ID (incluindo táticas)
        strategy_map = {
            str(item["id"]): {
                "name": item["name"],
                "tatics": item.get("tatics", [])  # Inclui lista de táticas com name, time e description
            }
            for item in strategies_data
        }

        # Substitui os IDs de estratégias por objetos completos
        session["strategies"] = [
            strategy_map.get(str(sid), {
                "name": f"ID {sid}",
                "tatics": []
            })
            for sid in session.get("strategies", [])
        ]

        full_tactics_time = 0
        for strategy in session["strategies"]:
            for tactic in strategy["tatics"]:
                # Adiciona o tempo de cada tática ao tempo total
                full_tactics_time += tactic.get("time", 0)

        session["full_tatics_time"] = full_tactics_time # Adiciona o tempo total de táticas à sessão

        # Busca nomes de professores e estudantes e domains
        teachers_data = requests.get(f"{USER_URL}/teachers").json()
        students_data = requests.get(f"{USER_URL}/students").json()
        domains_data = requests.get(f"{DOMAIN_URL}/domains").json()
        # return f"{domains_data}"
    
        teacher_map = {str(item["id"]): item["name"] for item in teachers_data}
        student_map = {str(item["id"]): item["name"] for item in students_data}
        domains_map = {str(item["id"]): item["name"] for item in domains_data}

        session["teachers"] = [teacher_map.get(str(tid), f"ID {tid}") for tid in session.get("teachers", [])]
        session["students"] = [student_map.get(str(sid), f"ID {sid}") for sid in session.get("students", [])]
        session["domains"] = [{"name": domains_map.get(str(sid), f"ID {sid}"), "id": sid} for sid in session.get("domains", [])]

        # return f"{session}"
        return render_template("control/show_session.html", session=session, current_user=current_user)

    except RequestException as e:
        return jsonify({"error": "Service unavailable", "details": str(e)}), 503


@session_bp.route('/sessions/delete/<int:session_id>', methods=['POST'])
@token_required
def delete_session(session_id, current_user=None):
    if request.form.get('_method') == 'DELETE':
        # Lógica para deletar a sessão
        response = requests.delete(f"{CONTROL_URL}/sessions/delete/{session_id}")
        if response.status_code == 200:
            return redirect(url_for('session.list_sessions'))
        else:
            return f"Erro ao deletar: {response.text}", response.status_code
        

@session_bp.route('/sessions/status/<int:session_id>', methods=['GET'])
@token_required
def get_session_status(session_id, current_user=None):
    try:
        response = requests.get(f"{CONTROL_URL}/sessions/status/{session_id}")
        return (response.text, response.status_code, response.headers.items())
    except RequestException as e:
        return jsonify({"error": "Control service unavailable", "details": str(e)}), 503


@session_bp.route('/sessions/start/<int:session_id>', methods=['GET'])
@token_required
def start_session(session_id, current_user=None):
    try:
        session_status = requests.get(f"{CONTROL_URL}/sessions/status/{session_id}").json()
        if(session_status["status"] == "in-progress"):
            return jsonify({"error": "Session already in progress"}), 400
        
        response = requests.post(f"{CONTROL_URL}/sessions/start/{session_id}")
        return (response.text, response.status_code, response.headers.items())
    except RequestException as e:
        return jsonify({"error": "Control service unavailable", "details": str(e)}), 503


@session_bp.route('/sessions/end/<int:session_id>', methods=['GET'])
@token_required
def end_session(session_id, current_user=None):
    try:
        response = requests.post(f"{CONTROL_URL}/sessions/end/{session_id}")
        return (response.text, response.status_code, response.headers.items())
    except RequestException as e:
        return jsonify({"error": "Control service unavailable", "details": str(e)}), 503
    


@session_bp.route('/sessions/<int:session_id>/current_tactic', methods=['GET'])
def get_current_tactic(session_id):
    # Buscar a sessão
    session_response = requests.get(f"{CONTROL_URL}/sessions/{session_id}")
    # return (session_response.text, session_response.status_code, session_response.headers.items())

    if session_response.status_code != 200:
        return jsonify({'error': 'Session not found'}), 404

    session_json = session_response.json()

    if session_json['status'] != 'in-progress' or not session_json.get("start_time"):
        return jsonify({'message': 'Session not started'}), 400

    # Converter start_time para datetime (assumindo formato ISO 8601)
    start_time = datetime.strptime(session_json["start_time"], "%a, %d %b %Y %H:%M:%S %Z")
    elapsed_time = (datetime.utcnow() - start_time).total_seconds()
    elapsed_minutes = elapsed_time / 60


    tactics = []
    for strategy_id in session_json['strategies']:
        strategy_response = requests.get(f"{STRATEGIES_URL}/strategies/{strategy_id}")
        # return f"{strategy_response.text}"
        if strategy_response.status_code != 200:
            continue

        strategy_data = strategy_response.json()
        strategy_tactics = strategy_data.get('tatics', [])
        tactics.extend(strategy_tactics)

    # return f"{tactics}"
    

    total_elapsed = 0
    for tactic in tactics:
        duration = tactic.get('time', 0)
        if elapsed_minutes < total_elapsed + duration:
            remaining = (total_elapsed + duration - elapsed_minutes) * 60
            return jsonify({
                'tactic': {
                    'name': tactic['name'],
                    'description': tactic.get('description', ''),
                    'total_time': duration * 60
                },
                'remaining_time': int(remaining),
                'elapsed_time': int(elapsed_time),
                'strategy_tactics': tactics
            })

        total_elapsed += duration

    
    # Se todas as táticas foram concluídas, finalizar a sessão
    requests.post(f"{CONTROL_URL}/sessions/end/{session_id}")

    # return f"{session_response.text}"

    return jsonify({'message': 'All tactics completed'})

