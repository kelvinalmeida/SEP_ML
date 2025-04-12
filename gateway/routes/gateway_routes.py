from flask import Blueprint, jsonify, render_template, request, redirect, url_for, make_response
import requests
from requests.exceptions import RequestException
from functools import wraps
import jwt


gateway_bp = Blueprint('gateway_bp', __name__)

USER_URL = 'http://user:5002'
CONTROL_URL = 'http://controller:5001'
# USER_URL = 'http://localhost:5002'
# CONTROL_URL = 'http://localhost:5001'

SECRET_KEY = "sua_chave_super_secreta"


# @app.context_processor
# def inject_current_user():
#     token = request.cookies.get("access_token")
#     current_user = None

#     if token:
#         try:
#             current_user = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
#         except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
#             current_user = None

#     return dict(current_user=current_user)


def verificar_cookie():
    token = request.cookies.get("access_token")
    current_user = None

    if token:
        try:
            current_user = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            print("Token decodificado:", current_user)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            current_user = None
            print("Token inválido ou expirado")

    return current_user

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("access_token")
        if not token:
            return redirect(url_for('gateway_bp.login'))

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            # Passa o payload (informações do usuário) como argumento extra
            return f(*args, **kwargs, current_user=payload)
        except jwt.ExpiredSignatureError:
            return redirect(url_for('gateway_bp.login'))
        except jwt.InvalidTokenError:
            return redirect(url_for('gateway_bp.login'))

    return decorated


@gateway_bp.route("/")
def home_page():
    print("Entrou na home")
    current_user = verificar_cookie()

    if current_user:
        # Se o usuário estiver autenticado, redireciona para a página de inicial
        return render_template("dashboard.html", current_user=current_user)
    
    return render_template("start.html")


@gateway_bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            response = requests.post(f"{USER_URL}/login", json={"username": username, "password": password})
            if response.status_code == 200:
                token = response.json().get("token")
                
                # Criar resposta com cookie
                resp = make_response(redirect(url_for('gateway_bp.home_page')))  # exemplo
                resp.set_cookie('access_token', token, httponly=True, max_age=3600)  # 1 hora
                return resp
            else:
                return render_template("login.html", error="Login failed.")
        except RequestException as e:
            return render_template("login.html", error="User service unavailable.")
    
    return render_template("login.html")

@gateway_bp.route('/logout')
def logout():
    # Criar uma resposta redirecionando para a tela de login
    resp = make_response(redirect(url_for('gateway_bp.home_page')))
    
    # Remover o cookie do token
    resp.set_cookie('access_token', '', expires=0)
    
    return resp


@gateway_bp.route('/perfil')
@token_required
def perfil(current_user=None):
    # print(current_user)
    user_id = current_user['id']
    url = f"{USER_URL}/students/{user_id}"
    # print("dsadasdasdasd" + url)
    response = requests.get(url)
    user = response.json()
    return render_template('perfil.html', user=user)


# ===========================
# 👨‍🎓 STUDENT ENDPOINTS
# ===========================

@gateway_bp.route('/students/create', methods=['POST', 'GET'])
def create_students():
    if request.method == 'POST':
        # Get the form data
        name = request.form["name"]
        age = request.form["age"]
        course = request.form["course"]
        type = "student"
        username = request.form["username"]
        password = request.form["password"]

        student = {"name": name, "age": age, "course": course, "type": type, "username": username, "password": password}
        
        try:
            response = requests.post(f"{USER_URL}/students/create", json=student)
            if response.status_code == 200:
                json_response = response.json()
                return jsonify(json_response), 200
            else:
                return jsonify({"error": "Failed to create student", "details": response.text}), response.status_code
        except RequestException as e:
            return jsonify({"error": "User service unavailable", "details": str(e)}), 503
    
    return render_template("./user/create_student.html")
    

@gateway_bp.route('/students', methods=['GET'])
@token_required
def get_students():
    try:
        response = requests.get(f"{USER_URL}/students")
        students = response.json()  # pega o JSON
        return render_template("./user/list_students.html", students=students)
    except RequestException as e:
        return jsonify({"error": "User service unavailable", "details": str(e)}), 503


@gateway_bp.route('/students/<int:student_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def get_student_by_id(student_id):
    try:
        url = f"{USER_URL}/students/{student_id}"
        if request.method == 'GET':
            response = requests.get(url)
        elif request.method == 'PUT':
            response = requests.put(url, json=request.get_json())
        elif request.method == 'DELETE':
            response = requests.delete(url)
        return jsonify(response.json()), response.status_code
    except RequestException as e:
        return jsonify({"error": "User service unavailable", "details": str(e)}), 503


# ===========================
# 👨‍🏫 TEACHER ENDPOINTS
# ===========================

@gateway_bp.route('/teachers/create', methods=['POST', 'GET'])
def create_teacher(current_user=None):
    if request.method == 'POST':
        # Get the form data
        name = request.form["name"]
        age = request.form["age"]
        type = "teacher"
        username = request.form["username"]
        password = request.form["password"]

        teacher = {"name": name, "age": age, "type": type, "username": username, "password": password}
        
        try:
            response = requests.post(f"{USER_URL}/teachers/create", json=teacher)
            if response.status_code == 200:
                json_response = response.json()
                return jsonify(json_response), 200
            else:
                return jsonify({"error": "Failed to create teacher", "details": response.text}), response.status_code
        except RequestException as e:
            return jsonify({"error": "User service unavailable", "details": str(e)}), 503
    
    return render_template("./user/create_teacher.html")

@gateway_bp.route('/teachers', methods=['GET'])
@token_required
def get_teachers():
    try:
        response = requests.get(f"{USER_URL}/teachers")
        teachers = response.json()  # pega o JSON
        return render_template("./user/list_teachers.html", teachers=teachers)
    except RequestException as e:
        return jsonify({"error": "User service unavailable", "details": str(e)}), 503


@gateway_bp.route('/teachers/<int:teacher_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def handle_teacher(teacher_id):
    try:
        url = f"{USER_URL}/teachers/{teacher_id}"
        if request.method == 'GET':
            response = requests.get(url)
        elif request.method == 'PUT':
            response = requests.put(url, json=request.get_json())
        elif request.method == 'DELETE':
            response = requests.delete(url)
        return (response.text, response.status_code, response.headers.items())
    except RequestException as e:
        return jsonify({"error": "User service unavailable", "details": str(e)}), 503


# ===========================
# 🧠 SESSION ENDPOINTS
# ===========================

@gateway_bp.route('/sessions/create', methods=['GET', "POST"])
@token_required
def create():
    if request.method == 'POST':
        try:
            strategy = request.form.get('strategy')
            response = requests.post(f"{CONTROL_URL}/sessions/create", json={"strategy": strategy})
            if response.status_code == 200:
                sessions = response.json()  # pega o JSON
                return jsonify(sessions), 200
            else:
                return f"Erro ao buscar sessões: {response.status_code}", response.status_code
        except RequestException as e:
            return jsonify({"error": "Control service unavailable", "details": str(e)}), 503
    else:
        return render_template("./control/create_session.html")

@gateway_bp.route('/sessions', methods=['GET'])
@token_required
def list_sessions():
    try:
        response = requests.get(f"{CONTROL_URL}/sessions")
        if response.status_code == 200:
            sessions = response.json()  # pega o JSON
            return render_template("./control/list_all_sessions.html", sessions=sessions)
        else:
            return f"Erro ao buscar sessões: {response.status_code}", response.status_code
    except RequestException as e:
        return jsonify({"error": "Control service unavailable", "details": str(e)}), 503


@gateway_bp.route('/sessions/status/<int:session_id>', methods=['GET'])
@token_required
def get_session_status(session_id):
    try:
        response = requests.get(f"{CONTROL_URL}/sessions/status/{session_id}")
        return (response.text, response.status_code, response.headers.items())
    except RequestException as e:
        return jsonify({"error": "Control service unavailable", "details": str(e)}), 503


@gateway_bp.route('/sessions/start/<int:session_id>', methods=['POST'])
@token_required
def start_session(session_id):
    try:
        response = requests.post(f"{CONTROL_URL}/sessions/start/{session_id}")
        return (response.text, response.status_code, response.headers.items())
    except RequestException as e:
        return jsonify({"error": "Control service unavailable", "details": str(e)}), 503


@gateway_bp.route('/sessions/end/<int:session_id>', methods=['POST'])
@token_required
def end_session(session_id):
    try:
        response = requests.post(f"{CONTROL_URL}/sessions/end/{session_id}")
        return (response.text, response.status_code, response.headers.items())
    except RequestException as e:
        return jsonify({"error": "Control service unavailable", "details": str(e)}), 503
