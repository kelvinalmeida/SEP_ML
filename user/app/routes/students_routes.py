from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from ..models import Student
from .. import db

student_bp = Blueprint("student_bp", __name__)

@student_bp.route("/students/create", methods=["GET", "POST"])
def create_student():
    if request.method == "POST":
        name = request.json["name"]
        age = request.json["age"]
        course = request.json["course"]
        type = "student"
        username = request.json["username"]
        password = request.json["password"]

        student = Student(name=name, age=age, course=course, type=type, username=username, password_hash=password)
        db.session.add(student)
        db.session.commit()
        return jsonify({"message": "Aluno criado com sucesso!"}), 200

    return jsonify({"error": "Método não permitido"}), 405

@student_bp.route("/students", methods=["GET"])
def get_students(): 
    students = Student.query.all()
    return jsonify([{"id": s.id, "name": s.name, "age": s.age, "course": s.course, "type": s.type, "username": s.username, "password": s.password_hash} for s in students])

@student_bp.route("/students/<int:student_id>", methods=["GET"])
def get_student_by_id(student_id):
    student = Student.query.get(student_id)
    if student:
        return jsonify({"id": student.id, "name": student.name, "age": student.age, "course": student.course})
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

@student_bp.route('/students/ids_to_names', methods=['GET'])
def ids_to_names():
    ids = request.args.getlist('ids')
    
    if not ids:
        return jsonify({"error": "No IDs provided"}), 400

    try:
        # converte todos os ids para inteiros
        ids = list(map(int, ids))
    except ValueError:
        return jsonify({"error": "IDs must be integers"}), 400

    students = Student.query.filter(Student.id.in_(ids)).all()

    if not students:
        return jsonify({"error": "No students found"}), 404

    result = [ 
        strategy.name
        for strategy in students ]

    return jsonify(result), 200