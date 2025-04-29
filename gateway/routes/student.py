from flask import Blueprint, render_template, request, jsonify
from requests.exceptions import RequestException
import requests
from .auth import token_required
from .services_routs import USER_URL

student_bp = Blueprint("student", __name__)

@student_bp.route('/students/create', methods=['POST', 'GET'])
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
    

@student_bp.route('/students', methods=['GET'])
@token_required
def get_students(current_user=None):
    try:
        response = requests.get(f"{USER_URL}/students")
        students = response.json()  # pega o JSON
        return render_template("./user/list_students.html", students=students)
    except RequestException as e:
        return jsonify({"error": "User service unavailable", "details": str(e)}), 503


@student_bp.route('/students/<int:student_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def get_student_by_id(student_id, current_user=None):
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