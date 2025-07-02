import jwt
import datetime
from flask import Blueprint, request, jsonify, current_app
from ..models import Student, Teacher

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user_student = Student.query.filter_by(username=username).first()
    user_teacher = Teacher.query.filter_by(username=username).first()
    
    if user_student:
        user = user_student
    else:
        user = user_teacher

    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # print(f"User found: {user.username}, Type: {user.type}, password: {user.password_hash}")

    if user and user.check_password(password):
        token = jwt.encode({
            'id': user.id,
            'type': user.type,
            'username': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})

    return jsonify({'error': 'Invalid credentials'}), 401
