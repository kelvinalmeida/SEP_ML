from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from ..models import Teacher
from .. import db

teachers_bp = Blueprint("teachers_bp", __name__)
# ============================
# 👨‍🏫 ENDPOINTS PARA PROFESSORES
# ============================
@teachers_bp.route("/teachers/create", methods=["GET", "POST"])
def create_teacher():

    if(request.method == "POST"):
        name = request.json["name"]
        age = request.json["age"]
        type = "teacher"
        username = request.json["username"]
        password = request.json["password"]

        teacher = Teacher(name=name, age=age, type=type, username=username, password_hash=password)
        db.session.add(teacher)
        db.session.commit()
        return jsonify({"message": "Professor criado com sucesso!"}), 200  # Retorna uma mensagem de sucesso
    
    return jsonify({"error": "Método não permitido"}), 405  # Retorna um erro se o método não for POST
    

@teachers_bp.route("/teachers", methods=["GET"])
def get_teachers():
    teachers = Teacher.query.all()
    return jsonify([{"id": t.id, "name": t.name, "age": t.age, "type": t.type} for t in teachers])

@teachers_bp.route("/teachers/<int:teacher_id>", methods=["GET"])
def get_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if teacher:
        return jsonify({"id": teacher.id, "name": teacher.name, "age": teacher.age, "type": teacher.type})
    return jsonify({"error": "Professor não encontrado"}), 404

@teachers_bp.route("/teachers/<int:teacher_id>", methods=["PUT"])
def update_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if teacher:
        data = request.get_json()
        teacher.name = data.get("name", teacher.name)
        teacher.age = data.get("age", teacher.age)
        db.session.commit()
        return jsonify({"message": "Professor atualizado!", "teacher": data})
    return jsonify({"error": "Professor não encontrado"}), 404

@teachers_bp.route("/teachers/<int:teacher_id>", methods=["DELETE"])
def delete_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if teacher:
        db.session.delete(teacher)
        db.session.commit()
        return jsonify({"message": "Professor deletado!"})
    return jsonify({"error": "Professor não encontrado"}), 404