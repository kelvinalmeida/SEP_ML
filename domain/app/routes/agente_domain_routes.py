import json
import logging
import sys
import os
from flask import request, redirect, url_for, render_template, send_file, Blueprint, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from db import create_connection

agente_domain_bp = Blueprint('agente_domain_bp', __name__)


# Adicione esta nova rota para servir como "Memória" para o Agente
import json
import logging
import sys
import os
from flask import request, redirect, url_for, render_template, send_file, Blueprint, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from db import create_connection
from pypdf import PdfReader  # Certifique-se de instalar: pip install pypdf

agente_domain_bp = Blueprint('agente_domain_bp', __name__)

def get_db_connection():
    """Helper para conectar ao banco usando a config da app"""
    return create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

@agente_domain_bp.route('/get_content/<int:id>', methods=['GET'])
def get_article_content(id):
    """
    Recupera o conteúdo de um PDF pelo ID.
    
    Parâmetros opcionais na URL (query string):
    - format=pdf : Retorna o arquivo PDF para download/visualização.
    - format=text (padrão): Retorna um JSON com o texto extraído do PDF.

    Parâmetro format:

    GET /get_content/1 -> Retorna JSON com o texto (ideal para RAG/LLMs).

    GET /get_content/1?format=pdf -> Retorna o arquivo binário (para download ou visualização direta).
    
    """
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 503
    
    cursor = conn.cursor()
    try:
        # 1. Busca os metadados do PDF no banco
        cursor.execute("SELECT filename, description, path FROM rag_library WHERE id = %s", (id,))
        pdf = cursor.fetchone()
        
        if not pdf:
            return jsonify({"error": "PDF não encontrado no banco de dados."}), 404

        filename = pdf['filename']
        db_path = pdf['path']
        
        # 2. Determina o caminho real do arquivo
        # Tenta primeiro o caminho salvo no banco (geralmente em 'uploads')
        file_path = db_path
        if not os.path.exists(file_path):
            # Se não achar, tenta corrigir o caminho relativo se necessário
            if not os.path.isabs(file_path):
                file_path = os.path.join(current_app.root_path, 'uploads', filename)

        # Se ainda não existir, tenta na pasta 'RAG_arquivos_compartilhados' conforme solicitado
        if not os.path.exists(file_path):
            rag_path = os.path.join(current_app.root_path, 'RAG_arquivos_compartilhados', filename)
            if os.path.exists(rag_path):
                file_path = rag_path
        
        # Verificação final
        if not os.path.exists(file_path):
            return jsonify({"error": f"Arquivo físico não encontrado: {filename}"}), 404

        # 3. Verifica o formato solicitado (texto ou arquivo)
        request_format = request.args.get('format', 'text')

        if request_format == 'pdf':
            # Retorna o próprio arquivo PDF
            return send_file(file_path, as_attachment=False)
        
        else:
            # Padrão: Extrai o texto do PDF para o Agente
            try:
                reader = PdfReader(file_path)
                text_content = ""
                for page in reader.pages:
                    text_content += page.extract_text() + "\n"
                
                return jsonify({
                    "id": id,
                    "filename": filename,
                    "description": pdf.get('description'),
                    "content": text_content.strip()
                })
            except Exception as e:
                return jsonify({"error": f"Erro ao ler o PDF: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()