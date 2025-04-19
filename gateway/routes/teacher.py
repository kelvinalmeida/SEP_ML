from flask import Blueprint, render_template, request, jsonify
from requests.exceptions import RequestException

import requests
from .auth import token_required
from .services_routs import USER_URL

teacher_bp = Blueprint("teacher", __name__)

@teacher_bp.route('/teachers/create', methods=['POST', 'GET'])
def create_teacher():
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

@teacher_bp.route('/teachers', methods=['GET'])
@token_required
def get_teachers(current_user=None):
    try:
        response = requests.get(f"{USER_URL}/teachers")
        teachers = response.json()  # pega o JSON
        return render_template("./user/list_teachers.html", teachers=teachers)
    except RequestException as e:
        return jsonify({"error": "User service unavailable", "details": str(e)}), 503


@teacher_bp.route('/teachers/<int:teacher_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def handle_teacher(teacher_id, current_user=None):
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