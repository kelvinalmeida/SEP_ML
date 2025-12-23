import logging
import os
from flask import Blueprint, request, jsonify
from google import genai
from config import Config

# Tentativa de importação relativa ou absoluta do db.py, 
# seguindo o padrão que você usa no 'control'
try:
    from db import create_connection
except ImportError:
    from ...db import create_connection

agente_user_bp = Blueprint('agente_user_bp', __name__)

@agente_user_bp.route('/students/summarize_preferences', methods=['POST'])
def summarize_preferences():
    """
    Agente User: Recebe IDs, busca via SQL Direto (psycopg2) e resume com Gemini.
    """
    data = request.get_json()
    student_ids = data.get('student_ids', [])

    if not student_ids:
        return jsonify({"summary": "Nenhum estudante selecionado."}), 200

    conn = None
    try:
        # 1. Conexão
        db_url = getattr(Config, 'SQLALCHEMY_DATABASE_URI', os.getenv('DATABASE_URL'))
        conn = create_connection(db_url)
        
        if not conn:
             return jsonify({"error": "Falha na conexão com o banco de dados"}), 500

        students_data = []
        
        with conn.cursor() as cur:
            # 2. Query SQL Atualizada (Incluindo pref_receive_email)
            query = """
                SELECT name, pref_content_type, pref_communication, pref_receive_email
                FROM student 
                WHERE student_id = ANY(%s)
            """
            cur.execute(query, (student_ids,))
            students_data = cur.fetchall()

        if not students_data:
            return jsonify({"summary": "Estudantes não encontrados na base de dados."}), 404

        # 3. Formatação do Texto (Tratando o Booleano)
        profiles_text = []
        for s in students_data:
            name = s.get('name', 'Aluno')
            p_type = s.get('pref_content_type') or 'Não informado'
            p_comm = s.get('pref_communication') or 'Não informado'
            
            # Lógica para o campo booleano
            recebe_email = s.get('pref_receive_email')
            txt_email = "Aceita receber emails" if recebe_email else "NÃO aceita emails"
            
            profiles_text.append(f"- Aluno {name}: Prefere '{p_type}' via '{p_comm}'. {txt_email}.")
        
        profiles_joined = "\n".join(profiles_text)

        # return jsonify({"profiles": profiles_joined}), 200

        # 4. Prompt Atualizado
        prompt = f"""
        Atue como um Especialista Pedagógico.
        Analise estas preferências de aprendizado reais recuperadas do banco de dados:
        {profiles_joined}
        
        Gere um resumo curto (máximo 1 parágrafo) sobre o perfil da turma. 
        Destaque qual tipo de mídia e canal é o mais efetivo.
        IMPORTANTE: Cite explicitamente se o uso de email é viável para a maioria ou se deve ser evitado.
        """

        client = genai.Client(api_key=Config.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )

        return jsonify({
            "summary": response.text,
            "student_count": len(students_data)
        }), 200

    except Exception as e:
        logging.error(f"Erro no Agente User: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()