import json
import logging
import sys
import os
from flask import request, redirect, url_for, render_template, send_file, Blueprint, jsonify, current_app
from werkzeug.utils import secure_filename
from flask import send_from_directory
from db import create_connection

domain_bp = Blueprint('domain_bp', __name__)

# Configuração da pasta de uploads (caso ainda não exista no app config)
# UPLOAD_FOLDER será definido dentro da rota usando current_app

@domain_bp.route('/domains/create', methods=['POST'])
def create_domain():
    UPLOAD_FOLDER = os.path.join(current_app.root_path, 'uploads')
    
    # Garante que a pasta existe (boa prática ao lidar com arquivos)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Conexão com o banco
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 503
    
    cursor = conn.cursor()

    try:
        # 1. Coleta dados do formulário
        name = request.form.get('name')
        description = request.form.get('description')
        exercises_raw = request.form.get('exercises')
        
        youtube_links = request.form.getlist('youtube_link')
        pdf_files = request.files.getlist("pdfs")
        video_files = request.files.getlist("video")

        # 2. Criação do domínio (INSERT pai)
        # Usamos RETURNING id para pegar o ID gerado pelo Serial/Identity do Postgres
        query_domain = """
            INSERT INTO domain (name, description) 
            VALUES (%s, %s) 
            RETURNING id;
        """
        cursor.execute(query_domain, (name, description))
        domain_row = cursor.fetchone()
        new_domain_id = domain_row['id'] # Assumindo RealDictCursor

        # 3. Salva PDFs
        for file in pdf_files:
            if file and file.filename.endswith('.pdf'):
                filename = secure_filename(file.filename)
                path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(path)

                query_pdf = """
                    INSERT INTO pdf (filename, path, domain_id) 
                    VALUES (%s, %s, %s);
                """
                cursor.execute(query_pdf, (filename, path, new_domain_id))

        # 4. Salva vídeos enviados (Upload)
        for video_file in video_files:
            if video_file and video_file.filename.endswith('.mp4'):
                filename = secure_filename(video_file.filename)
                path = os.path.join(UPLOAD_FOLDER, filename)
                video_file.save(path)

                query_video_upload = """
                    INSERT INTO video_upload (filename, path, domain_id) 
                    VALUES (%s, %s, %s);
                """
                cursor.execute(query_video_upload, (filename, path, new_domain_id))

        # 5. Salva links do YouTube
        for yt_url in youtube_links:
            yt_url = yt_url.strip()
            if yt_url:
                query_video_yt = """
                    INSERT INTO video_youtube (url, domain_id) 
                    VALUES (%s, %s);
                """
                cursor.execute(query_video_yt, (yt_url, new_domain_id))

        # 6. Salva exercícios
        if exercises_raw:
            exercises = json.loads(exercises_raw)
            for ex in exercises:
                question = ex.get("question", "").strip()
                options = ex.get("options", [])
                correct = ex.get("correct", "").strip()

                if question and options and correct:
                    # json.dumps(options) converte a lista Python para String JSON
                    # O Postgres aceita isso nativamente em campos JSONB ou TEXT
                    query_exercise = """
                        INSERT INTO exercise (question, options, correct, domain_id) 
                        VALUES (%s, %s, %s, %s);
                    """
                    cursor.execute(query_exercise, (
                        question, 
                        json.dumps(options), 
                        correct, 
                        new_domain_id
                    ))

        # 7. Commit final da transação
        conn.commit()
        
        cursor.close()
        conn.close()

        return jsonify({"message": "Domain created successfully!"}), 200

    except Exception as e:
        # Em caso de erro (no banco ou no salvamento de arquivos), desfaz as alterações no banco
        if conn:
            conn.rollback()
            cursor.close()
            conn.close()
        return jsonify({"message": "Erro ao processar exercícios", "error": str(e)}), 400



# @domain_bp.route('/domains', methods=['GET'])
# def list_domains():
#     domains = Domain.query.all()
#     domains_json = [domain.to_dict() for domain in domains]
#     return domains_json, 200

# @domain_bp.route('/domains/delete/<int:domain_id>', methods=['DELETE'])
# def delete_domain(domain_id):
#     domain = Domain.query.get_or_404(domain_id)
    
#     # Delete associated PDFs
#     for pdf in domain.pdfs:
#         if os.path.exists(pdf.path):
#             os.remove(pdf.path)
#         db.session.delete(pdf)

#     # Delete associated videos
#     for video in domain.videos_uploaded:
#         if os.path.exists(video.path):
#             os.remove(video.path)
#         db.session.delete(video)
#     for video in domain.videos_youtube:
#         db.session.delete(video)    
#     # Delete associated exercises
#     for exercise in domain.exercises:
#         db.session.delete(exercise)

#     db.session.delete(domain)
#     db.session.commit()
    
#     return jsonify({"message": "Domain deleted successfully!"}), 200


# @domain_bp.route('/domains/<int:domain_id>', methods=['GET'])
# def get_domain(domain_id):
#     domain = Domain.query.get_or_404(domain_id)
#     return jsonify(domain.to_dict()), 200


# @domain_bp.route('/pdfs', methods=['GET'])
# def list_pdfs():
#     pdfs = PDF.query.all()
#     pdfs_json = [pdf.to_dict() for pdf in pdfs]
#     return jsonify(pdfs_json), 200


# @domain_bp.route('/pdfs/<int:pdf_id>', methods=['GET'])
# def download_pdf(pdf_id):
#     # return "oi"
#     try:
#         pdf = PDF.query.get_or_404(pdf_id)
        
#         # Usa caminho absoluto
#         file_path = os.path.abspath(pdf.path)
#         # return f"{file_path}"
#         if not os.path.exists(file_path):
#             return jsonify({'error': 'File not found'}), 404

#         return send_file(file_path, as_attachment=True)
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @domain_bp.route('/domains/ids_to_names', methods=['GET'])
# def ids_to_names():
#     ids = request.args.getlist('ids')
    
#     if not ids:
#         return jsonify([]), 200

#     try:
#         # converte todos os ids para inteiros
#         ids = list(map(int, ids))
#     except ValueError:
#         return jsonify({"error": "IDs must be integers"}), 400

#     domains = Domain.query.filter(Domain.id.in_(ids)).all()

#     if not domains:
#         return jsonify({"error": "No domains found"}), 404

#     result = [ 
#         domain.to_dict()
#         for domain in domains ]

#     return jsonify(result), 200


# @domain_bp.route('/domains/<int:domain_id>/exercises', methods=['GET'])
# def get_domain_exercises(domain_id):
#     domain = Domain.query.get_or_404(domain_id)
#     return jsonify([exercise.to_dict() for exercise in domain.exercises]), 200



# @domain_bp.route('/domains/<int:domain_id>/videos', methods=['GET'])
# def get_domain_videos(domain_id):
#     domain = Domain.query.get_or_404(domain_id)
#     return jsonify({
#         "videos_uploaded": [video.to_dict() for video in domain.videos_uploaded],
#         "videos_youtube": [video.to_dict() for video in domain.videos_youtube],
#     }), 200


# @domain_bp.route('/video/uploaded/<int:video_id>', methods=['GET'])
# def get_uploaded_video(video_id):

#     UPLOAD_FOLDER = os.path.join(current_app.root_path, 'uploads')

#     video = VideoUpload.query.get_or_404(video_id)
    
#     filename = video.filename  # supondo que sua classe VideoUpload tenha um campo `filename`
#     filepath = os.path.join(UPLOAD_FOLDER, filename)
    
#     if not os.path.exists(filepath):
#         return jsonify({'error': 'File not found on server'}), 404
    
#     return send_from_directory(UPLOAD_FOLDER, filename)


# @domain_bp.route('/exerc/testscores', methods=['POST'])
# def get_test_scores():
#     request_data = request.json

#     logging.basicConfig(level=logging.INFO)
#     logging.info("🔍 Dados recebidos domain: %s", request_data)
#     sys.stdout.flush()

#     student_name = request_data.get('student_name')
#     student_id = request_data.get('student_id')
#     answers = request_data.get('answers') # Array de respostas do aluno

#     score = 0;

#     for answer in answers:
#         exercise = Exercise.query.get_or_404(answer['exercise_id'])

#         # logging.basicConfig(level=logging.INFO)
#         # print("answer['answer'] == exercise.correct", answer['answer'], exercise.correct)
#         # print("answer['answer'] == exercise.correct", int(answer['answer']) == int(exercise.correct))
#         # sys.stdout.flush()

#         if int(answer['answer']) == int(exercise.correct):
#             answer['correct'] = True
#             score += 1
#         else:
#             answer['correct'] = False

    
#     playload = {
#         "student_name": student_name,
#         "student_id": student_id,
#         "answers": answers,
#         "score": score,
#     }


#     logging.basicConfig(level=logging.INFO)
#     logging.info("🔍 Respostas verificadas: %s", playload)
#     sys.stdout.flush()


#     return jsonify(playload), 200