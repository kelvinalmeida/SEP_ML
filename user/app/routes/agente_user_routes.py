import json
import logging
import os
from flask import Blueprint, request, jsonify
from google import genai
from openai import OpenAI
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

        # 1. Prompt Simplificado (Pede apenas texto)
        prompt = f"""
        Atue como um Especialista Pedagógico.
        Analise estas preferências de aprendizado reais:
        {profiles_joined}
        
        OBJETIVO:
        Escreva um parágrafo único e conciso resumindo o perfil da turma.
        Destaque a mídia e o canal mais efetivos.
        Diga explicitamente se o e-mail é um canal viável para a maioria.

        FORMATO DE SAÍDA:
        Apenas o texto corrido, sem formatação JSON, sem markdown e sem títulos.
        """

        # 4. Chamada LLM (Groq)
        client = OpenAI(
            api_key=Config.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
        
        # 2. Chamada LLM (Sem response_format JSON)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Você é um assistente pedagógico conciso."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2 
            # response_format removido para permitir texto livre
        )

        content_text = response.choices[0].message.content
        
        # Faz o parse da string para um dicionário Python antes de enviar
        try:
            summary_dict = json.loads(content_text)
        except json.JSONDecodeError:
            # Fallback se a IA falhar
            summary_dict = {
                "resumo": content_text,
                "perfil_turma": {},
                "uso_email": "Indeterminado"
            }

        # 4. Retorno (Agora 'summary' será um objeto aninhado, limpo)
        return jsonify({
            "summary": summary_dict,
            "student_count": len(students_data)
        }), 200
    
    except Exception as e:
        logging.error(f"Erro no Agente User: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()