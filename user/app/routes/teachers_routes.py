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
    return jsonify([{"id": t.id, "name": t.name, "age": t.age, "type": t.type, "username": t.username, "password": t.password_hash} for t in teachers])

@teachers_bp.route("/teachers/<int:teacher_id>", methods=["GET"])
def get_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if teacher:
        return jsonify({"id": teacher.id, "name": teacher.name, "age": teacher.age, "type": teacher.type, "username": teacher.username})
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


@teachers_bp.route('/teachers/ids_to_usernames', methods=['GET'])
def ids_to_names():
    ids = request.args.getlist('ids')
    
    if not ids:
        return jsonify({"error": "No IDs provided"}), 400

    try:
        # converte todos os ids para inteiros
        ids = list(map(int, ids))
    except ValueError:
        return jsonify({"error": "IDs must be integers"}), 400

    teachers = Teacher.query.filter(Teacher.id.in_(ids)).all()

    if not teachers:
        return jsonify({"error": "No teachers found"}), 404

    # result = [ 
    #     strategy.name
    #     for strategy in teachers ]
    
    result = { "usernames": [teacher.username for teacher in teachers],
               "ids_with_usernames": [{"username": teacher.username, "id": teacher.id, 'type': 'professor'} for teacher in teachers] }

    return jsonify(result), 200



@teachers_bp.route('/teachers/all_teachers_usernames', methods=['GET'])
def all_teachers_usernames():
    teachers = Teacher.query.all()
    
    if not teachers:
        return jsonify({"error": "No teachers found"}), 404

    usernames = [teacher.username for teacher in teachers]
    
    return jsonify({"usernames": usernames}), 200