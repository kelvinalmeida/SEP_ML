from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
from ..models import Student
from .. import db
from db import create_connection

student_bp = Blueprint("student_bp", __name__)

@student_bp.route("/students/create", methods=["GET", "POST"])
def create_student():

    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    cursor = conn.cursor()

    if request.method == "POST":

        try:
            name = request.json["name"]
            age = request.json["age"]
            course = request.json["course"]
            type = "student"
            email = request.json["email"]
            username = request.json["username"]
            password = request.json["password"]
            

            add_student_query = """INSERT INTO students (name, age, course, type, email, username, password_hash)
                                VALUES (%s, %s, %s, %s, %s, %s, %s);"""
            cursor.execute(add_student_query, (name, age, course, type, email, username, password))
            conn.commit()

            return jsonify({"message": "Aluno criado com sucesso!"}), 201
        
        except Exception as e:
            conn.rollback()
            cursor.close()
            return jsonify({"error": str(e)}), 400
            

        # student = Student(name=name, age=age, course=course, type=type, email=email, username=username, password_hash=password)
        # db.session.add(student)
        # db.session.commit()

    return jsonify({"error": "Método não permitido"}), 405

@student_bp.route("/students", methods=["GET"])
def get_students(): 
    students = Student.query.all()
    return jsonify([{"id": s.id, "name": s.name, "age": s.age, "course": s.course, "type": s.type, "username": s.username, "password": s.password_hash} for s in students])

@student_bp.route("/students/<int:student_id>", methods=["GET"])
def get_student_by_id(student_id):
    student = Student.query.get(student_id)
    if student:
        return jsonify({"id": student.id, "name": student.name, "age": student.age, "course": student.course, "username": student.username, "type": student.type})
    return jsonify({"error": "Aluno não encontrado"}), 404

@student_bp.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    student = Student.query.get(student_id)
    if student:
        data = request.get_json()
        student.name = data.get("name", student.name)
        student.age = data.get("age", student.age)
        student.course = data.get("course", student.course)
        db.session.commit()
        return jsonify({"message": "Aluno atualizado!", "student": data})
    return jsonify({"error": "Aluno não encontrado"}), 404

@student_bp.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    student = Student.query.get(student_id)
    if student:
        db.session.delete(student)
        db.session.commit()
        return jsonify({"message": "Aluno deletado!"})
    return jsonify({"error": "Aluno não encontrado"}), 404

@student_bp.route('/students/ids_to_usernames', methods=['GET'])
def ids_to_names():
    ids = request.args.getlist('ids')

    try:
        # converte todos os ids para inteiros
        ids = list(map(int, ids))
        students = Student.query.filter(Student.id.in_(ids)).all()

        result = { "usernames": [student.username for student in students],
                "ids_with_usernames": [{"username": student.username, "id": student.id, 'type': 'estudante'} for student in students] }

        return jsonify(result), 200
    
    except ValueError:
        result = { "usernames": [],
               "ids_with_usernames": [{"username": '', "id": '', 'type': 'estudante'}] }
        return jsonify(result), 200



@student_bp.route('/students/all_students_usernames', methods=['GET'])
def all_students_usernames():
    students = Student.query.all()
    
    # if not students:
    #     return jsonify({"error": "No students found"}), 404

    usernames = [student.username for student in students]
    # ids_with_usernames = [{"username": student.username, "id": student.id, 'type': 'estudante'} for student in students]

    return jsonify({"usernames": usernames}), 200