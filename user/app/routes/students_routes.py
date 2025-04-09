from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from ..models import Student
from .. import db

student_bp = Blueprint("student_bp", __name__)

@student_bp.route("/")
def index():
    return render_template("index.html")

@student_bp.route("/students/create", methods=["GET", "POST"])
def create_student():
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        course = request.form["course"]
        type = "student"

        student = Student(name=name, age=age, course=course, type=type)
        db.session.add(student)
        db.session.commit()
        return redirect(url_for('student_bp.success', type='aluno'))

    return render_template("create_student.html")

@student_bp.route("/success/<string:type>")
def success(type):
    return f'{type} criada com sucesso!'

@student_bp.route("/students", methods=["GET"])
def get_students():
    students = Student.query.all()
    return jsonify([{"id": s.id, "name": s.name, "age": s.age, "course": s.course} for s in students])

@student_bp.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
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
