from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from ..models import Student, Teacher
from .. import db

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/students/create", methods=["GET", "POST"])
def create_student():
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        course = request.form["course"]
        type = "student"

        student = Student(name=name, age=age, course=course, type=type)
        db.session.add(student)
        db.session.commit()
        return redirect(url_for('main.success', type='aluno'))

    return render_template("create_student.html")

@main.route("/success/<string:type>")
def success(type):
    return f'{type} criada com sucesso!'

@main.route("/students", methods=["GET"])
def get_students():
    students = Student.query.all()
    return jsonify([{"id": s.id, "name": s.name, "age": s.age, "course": s.course} for s in students])

@main.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    student = Student.query.get(student_id)
    if student:
        return jsonify({"id": student.id, "name": student.name, "age": student.age, "course": student.course})
    return jsonify({"error": "Aluno não encontrado"}), 404

@main.route("/students/<int:student_id>", methods=["PUT"])
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

@main.route("/students", methods=["DELETE"])
def delete_student(student_id):
    student = Student.query.get(student_id)
    if student:
        db.session.delete(student)
        db.session.commit()
        return jsonify({"message": "Aluno deletado!"})
    return jsonify({"error": "Aluno não encontrado"}), 404

# ============================
# 👨‍🏫 ENDPOINTS PARA PROFESSORES
# ============================
@main.route("/teachers/create", methods=["GET", "POST"])
def create_teacher():

    if(request.method == "POST"):
        name = request.form["name"]
        age = request.form["age"]
        type = "teacher"

        teacher = Teacher(name=name, age=age, type=type)
        db.session.add(teacher)
        db.session.commit()
        return redirect(url_for('main.success', type='Professor'))
    
    return render_template("create_teacher.html"), 200  # Exibe o formulário 
    

@main.route("/teachers", methods=["GET"])
def get_teachers():
    teachers = Teacher.query.all()
    return jsonify([{"id": t.id, "name": t.name, "age": t.age, "type": t.type} for t in teachers])

@main.route("/teachers/<int:teacher_id>", methods=["GET"])
def get_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if teacher:
        return jsonify({"id": teacher.id, "name": teacher.name, "age": teacher.age, "type": teacher.type})
    return jsonify({"error": "Professor não encontrado"}), 404

@main.route("/teachers/<int:teacher_id>", methods=["PUT"])
def update_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if teacher:
        data = request.get_json()
        teacher.name = data.get("name", teacher.name)
        teacher.age = data.get("age", teacher.age)
        db.session.commit()
        return jsonify({"message": "Professor atualizado!", "teacher": data})
    return jsonify({"error": "Professor não encontrado"}), 404

@main.route("/teachers/<int:teacher_id>", methods=["DELETE"])
def delete_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if teacher:
        db.session.delete(teacher)
        db.session.commit()
        return jsonify({"message": "Professor deletado!"})
    return jsonify({"error": "Professor não encontrado"}), 404