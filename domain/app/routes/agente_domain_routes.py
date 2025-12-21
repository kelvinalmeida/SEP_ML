import json
import logging
import sys
import os
from flask import request, redirect, url_for, render_template, send_file, Blueprint, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from db import create_connection

agente_domain_bp = Blueprint('agente_domain_bp', __name__)


# Adicione esta nova rota para servir como "Memória" para o Agente
@agente_domain_bp.route('/get_content/<int:id>', methods=['GET'])
def get_article_content(id):
    """
    Simula a recuperação do texto de um PDF.
    Numa implementação real, você usaria uma lib como PyPDF2 aqui para ler o arquivo do disco.
    """
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 503
    
    cursor = conn.cursor()
    try:
        # Busca o PDF pelo ID
        cursor.execute("SELECT filename, description FROM pdf WHERE id = %s", (id,))
        pdf = cursor.fetchone()
        
        # Se não achar PDF com esse ID, pega o primeiro só para teste
        if not pdf:
            cursor.execute("SELECT filename, description FROM pdf LIMIT 1")
            pdf = cursor.fetchone()
            
        content_text = ""
        if pdf:
            # AQUI: Em produção, você leria o arquivo físico: open(path).read()
            # Como estamos simulando a "memória" do agente:
            content_text = f"Conteúdo extraído do arquivo {pdf['filename']}: Para uma estratégia eficaz de ensino de IA, o artigo recomenda fortemente o uso de 'Debate Sincrono' para fixação e 'Reuso' de materiais para eficiência. A nota deve ser alta apenas se houver interatividade."
        else:
            content_text = "Nenhum artigo de referência encontrado na base de conhecimento."

        return jsonify({"content": content_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
