import json
import logging
import sys
from urllib import response
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from requests.exceptions import RequestException
from flask import Response
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
                return render_template("/control/success.html")
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

        params = { 'ids': session.get("strategies", []) }
        strategies = requests.get(f"{STRATEGIES_URL}/strategies/ids_to_names", params=params).json()
        session["strategies"] = strategies  # Adiciona os nomes das estratégias à sessão
    

        all_tatics_time = requests.get(f"{STRATEGIES_URL}/strategies/full_tatics_time", params=params).json()
        session["full_tatics_time"] = all_tatics_time.get("full_tactics_time") # Adiciona o tempo total de táticas à sessão

        teachers_params = { 'ids': session.get("teachers", [])}
        teachers = requests.get(f"{USER_URL}/teachers/ids_to_usernames", params=teachers_params).json()
        session["teachers"] = teachers["usernames"] 

        students_params = { 'ids': session.get("students", [])}
        students = requests.get(f"{USER_URL}/students/ids_to_usernames", params=students_params).json()
        session["students"] = students["usernames"] 

        studantes_with_id_and_username = requests.get(f"{USER_URL}/students").json()
        session["students_ids_with_usernames"] = students['ids_with_usernames']

        domains_params = { 'ids': session.get("domains", [])}
        domains = requests.get(f"{DOMAIN_URL}/domains/ids_to_names", params=domains_params).json()
        session["domains"] = domains


        # return f"{session}"
        return render_template("control/show_session.html", session=session, current_user=current_user, studantes_with_id_and_username=studantes_with_id_and_username)

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
        return jsonify(response.json()), response.status_code
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
        return jsonify(response.json()), response.status_code
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



@session_bp.route("/sessions/submit_answer", methods=["POST"])
@token_required
def submit_answer(current_user=None):
    try:
        data = request.get_json()

        # Corrrige as respostas do exercício
        verified_answers = requests.post(f"{DOMAIN_URL}/exerc/testscores", json=data).json()

        playload = {
            "student_id": verified_answers["student_id"],
            "student_name": verified_answers["student_name"],
            "session_id": data["session_id"], 
            "answers": verified_answers["answers"],
            "score": verified_answers["score"]
        }

        logging.basicConfig(level=logging.INFO)
        logging.info("🔍 verified_answers: %s", playload)
        sys.stdout.flush()
        
        # Envia as respostas verificadas para o microserviço de controle
        resp = requests.post(f"{CONTROL_URL}/sessions/submit_answer", json=playload)

        if resp.status_code == 409:
            return jsonify({"resp": "As respostas já foram registradas para esse estudante!"}), 200

        # Por enquanto apenas retorna os dados recebidos
        return jsonify({"resp": "Respostas enviadas com sucesso!"}), 200

    except Exception as e:
        import traceback
        logging.info("❌ Erro interno no servidor:")
        traceback.print_exc()  # Mostra a stack completa do erro
        return jsonify({"error": str(e)}), 500
    

@session_bp.route("/studant/extranotes/<int:student_id>", methods=["POST"])
@token_required
def add_extra_notes(student_id, current_user=None):
    data = request.form.get("extra_notes")
    session_id = request.form.get("session_id")

    student = requests.get(f"{USER_URL}/students/{student_id}").json()

    playload = {
        "student_id": student.get("id"),
        "estudante_username": student.get("username"),
        "extra_notes": float(data),
        "session_id": session_id,
    }

    requests.post(f"{CONTROL_URL}/sessions/add_extra_notes", json=playload)

    return Response(status=204)
  

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
    
    # if(session_response["status"] == 'finished'):
    #     return jsonify({}), 200

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
                'strategy_tactics': tactics,
                'session_status': session_json['status'],
            })

        total_elapsed += duration

    
    # Se todas as táticas foram concluídas, finalizar a sessão
    requests.post(f"{CONTROL_URL}/sessions/end/{session_id}")

    # return f"{session_response.text}"

    return jsonify({'message': 'All tactics completed'})

