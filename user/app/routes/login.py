from flask import Blueprint, request, jsonify
from ..models import Student, Teacher

auth_bp = Blueprint("auth_bp", __name__)

# routes/auth.py ou dentro do auth_bp
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Busca no banco por student
    student = Student.query.filter_by(username=username).first()
    if student and student.check_password(password):
        return jsonify({"message": "Login successful", "role": "student", "user_id": student.id}), 200

    # Busca no banco por teacher se não achou como student
    teacher = Teacher.query.filter_by(username=username).first()
    if teacher and teacher.check_password(password):
        return jsonify({"message": "Login successful", "role": "teacher", "user_id": teacher.id}), 200

    return jsonify({"message": "Invalid username or password"}), 401

