from app import create_app

app = create_app()

print(app.url_map)

if __name__ == "__main__":
    app.run(debug=True)

# from flask import Flask, request, jsonify, url_for, render_template
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.utils import redirect

# app = Flask(__name__)

# # ============================
# # 🎲 CONFIGURAÇÃO DO BANCO DE DADOS
# # ============================
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"  # Altere para outro banco se necessário
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# db = SQLAlchemy(app)

# # ============================
# # 📌 MODELOS (ALUNOS & PROFESSORES)
# # ============================
# class Student(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     age = db.Column(db.Integer, nullable=False)
#     course = db.Column(db.String(100), nullable=False)
#     type = db.Column(db.String(100), nullable=False)

# class Teacher(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     subject = db.Column(db.String(100), nullable=False)
#     type = db.Column(db.String(100), nullable=False)

# # ============================
# # 📌 CRIA O BANCO DE DADOS (caso não exista)
# # ============================
# @app.before_request
# def create_tables():
#     db.create_all()

# # ============================
# # 🎓 ENDPOINTS PARA ALUNOS
# # ============================
# @app.route('/students/create', methods=['GET', 'POST'])
# def create_session():
#     if request.method == 'POST':
#         # Obtendo dados do formulário
#         name = request.form['name']
#         age = request.form['age']
#         course = request.form['course']
#         type = "student"

#         # Criando a nova sessão
#         new_student = Student(name=name, age=age, course=course, type=type)

#         # Adicionando a sessão ao banco de dados
#         db.session.add(new_student)
#         db.session.commit()

#         # Redirecionando para a página de sucesso
#         return redirect(url_for('success', type='aluno')), 201

#     return render_template('create_student.html')  # Exibe o formulário

# # Página de sucesso após a criação da sessão
# @app.route('/success/<string:type>')
# def success(type):
#     return f'{type} criada com sucesso!'

# @app.route("/students", methods=["GET"])
# def get_students():
#     students = Student.query.all()
#     return jsonify([{"id": s.id, "name": s.name, "age": s.age, "course": s.course} for s in students])

# @app.route("/students/<int:student_id>", methods=["GET"])
# def get_student(student_id):
#     student = Student.query.get(student_id)
#     if student:
#         return jsonify({"id": student.id, "name": student.name, "age": student.age, "course": student.course})
#     return jsonify({"error": "Aluno não encontrado"}), 404

# @app.route("/students/<int:student_id>", methods=["PUT"])
# def update_student(student_id):
#     student = Student.query.get(student_id)
#     if student:
#         data = request.get_json()
#         student.name = data.get("name", student.name)
#         student.age = data.get("age", student.age)
#         student.course = data.get("course", student.course)
#         db.session.commit()
#         return jsonify({"message": "Aluno atualizado!", "student": data})
#     return jsonify({"error": "Aluno não encontrado"}), 404

# @app.route("/students", methods=["DELETE"])
# def delete_student(student_id):
#     student = Student.query.get(student_id)
#     if student:
#         db.session.delete(student)
#         db.session.commit()
#         return jsonify({"message": "Aluno deletado!"})
#     return jsonify({"error": "Aluno não encontrado"}), 404

# # ============================
# # 👨‍🏫 ENDPOINTS PARA PROFESSORES
# # ============================
# @app.route("/teachers/create", methods=["GET", "POST"])
# def create_teacher():

#     if(request.method == "POST"):
#         name = request.form["name"]
#         subject = request.form["subject"]
#         type = "teacher"

#         teacher = Teacher(name=name, subject=subject, type=type)
#         db.session.add(teacher)
#         db.session.commit()
#         return redirect(url_for('success', type='Professor')), 201
    
#     return render_template("create_teacher.html"), 200  # Exibe o formulário
    

# @app.route("/teachers", methods=["GET"])
# def get_teachers():
#     teachers = Teacher.query.all()
#     return jsonify([{"id": t.id, "name": t.name, "subject": t.subject, "type": t.type} for t in teachers])

# @app.route("/teachers/<int:teacher_id>", methods=["GET"])
# def get_teacher(teacher_id):
#     teacher = Teacher.query.get(teacher_id)
#     if teacher:
#         return jsonify({"id": teacher.id, "name": teacher.name, "subject": teacher.subject, "experience": teacher.experience})
#     return jsonify({"error": "Professor não encontrado"}), 404

# @app.route("/teachers/<int:teacher_id>", methods=["PUT"])
# def update_teacher(teacher_id):
#     teacher = Teacher.query.get(teacher_id)
#     if teacher:
#         data = request.get_json()
#         teacher.name = data.get("name", teacher.name)
#         teacher.subject = data.get("subject", teacher.subject)
#         teacher.experience = data.get("experience", teacher.experience)
#         db.session.commit()
#         return jsonify({"message": "Professor atualizado!", "teacher": data})
#     return jsonify({"error": "Professor não encontrado"}), 404

# @app.route("/teachers/<int:teacher_id>", methods=["DELETE"])
# def delete_teacher(teacher_id):
#     teacher = Teacher.query.get(teacher_id)
#     if teacher:
#         db.session.delete(teacher)
#         db.session.commit()
#         return jsonify({"message": "Professor deletado!"})
#     return jsonify({"error": "Professor não encontrado"}), 404


# print(app.url_map)

# # ============================
# # 🚀 RODANDO O SERVIDOR
# # ============================
# if __name__ == "__main__":
#     app.run(debug=True)
