import json
import logging
import os
from flask import Blueprint, request, jsonify, current_app
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
            # Casting explícito para evitar erro "operator does not exist: integer = text"
            # O array chega como strings ['1', '2'], mas o banco espera inteiros.
            try:
                # Tenta converter para inteiros
                clean_ids = [int(x) for x in student_ids]
            except ValueError:
                # Se falhar (ex: ids alfanuméricos), mantém como string, mas o erro indicava INT no banco.
                clean_ids = student_ids

            query = """
                SELECT name, pref_content_type, pref_communication, pref_receive_email
                FROM student 
                WHERE student_id = ANY(%s)
            """
            cur.execute(query, (clean_ids,))
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



@agente_user_bp.route('/agent/generate_student_feedback', methods=['POST'])
def generate_student_feedback():
    """
    Gera um conselho pedagógico personalizado para o aluno.
    
    Payload Esperado:
    {
        "student_username": "kelvin",
        "session_id": 1,
        "domain": {
            "name": "Introdução a Python",
            "description": "Conceitos básicos de variáveis e loops"
        },
        "performance_data": { "notes": [80], "extra_notes": [1.0] },  <-- Do Control
        "chat_logs": { "general": ["Dúvida aqui"], "private": [] },   <-- Do Strategies
        "preferences": {                                              <-- Do User
            "pref_content_type": "exemplos",
            "pref_communication": "chat",
            "pref_receive_email": true
        }
    }
    """
    data = request.get_json()
    conn = None

    try:
        # 1. Extração de Dados
        username = data.get('student_username')
        session_id = data.get('session_id')
        domain = data.get('domain', {})
        performance = data.get('performance_data', {})
        chat = data.get('chat_logs', {})
        prefs = data.get('preferences', {})

        if not username:
            return jsonify({"error": "student_username é obrigatório"}), 400

        # 2. Configuração LLM
        if not Config.GROQ_API_KEY:
             return jsonify({"error": "GROQ_API_KEY não configurada"}), 500

        client = OpenAI(
            api_key=Config.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )

        # 3. Prompt
        prompt = f"""
        Atue como um Mentor Pedagógico Pessoal.
        Seu objetivo é dar um conselho curto e direto para o aluno melhorar seu desempenho.

        CONTEXTO DA AULA:
        - Tema: {domain.get('name', 'N/A')}
        - Descrição: {domain.get('description', 'N/A')}

        PERFIL DO ALUNO ({username}):
        - Prefere conteúdo do tipo: {prefs.get('pref_content_type', 'Indiferente')}
        - Prefere comunicação via: {prefs.get('pref_communication', 'Indiferente')}
        - Aceita dicas por email: {'Sim' if prefs.get('pref_receive_email') else 'Não'}

        DESEMPENHO:
        - Notas: {performance.get('notes', [])}
        - Extras: {performance.get('extra_notes', [])}

        CHAT:
        - Interações Gerais: {len(chat.get('general', []))}
        - Interações Privadas: {len(chat.get('private', []))}

        TAREFA:
        Escreva um feedback de 1 parágrafo (em português).
        1. Elogie pontos fortes.
        2. Aponte onde melhorar.
        3. Dê uma dica de estudo baseada na preferência dele.
        """

        # 4. Chamada LLM
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Você é um tutor amigável e motivador."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=300
        )

        feedback_text = response.choices[0].message.content

        # 5. Salvar no Banco de Dados (Correção Aqui)
        db_url = current_app.config.get("SQLALCHEMY_DATABASE_URI") or os.getenv("DATABASE_URL")
        conn = create_connection(db_url)
        
        new_id = None
        if conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO student_feedback 
                    (student_username, session_id, domain_name, feedback_content)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (username, session_id, domain.get('name'), feedback_text))
                
                new_row = cur.fetchone()
                
                # --- LÓGICA DE EXTRAÇÃO SEGURA ---
                if new_row:
                    if isinstance(new_row, dict):
                        # Se for dicionário (RealDictCursor)
                        new_id = new_row['id']
                    else:
                        # Se for Tupla
                        new_id = new_row[0]
                
                conn.commit()

        return jsonify({
            "status": "success",
            "student": username,
            "feedback": feedback_text,
            "feedback_id": new_id
        }), 200

    except Exception as e:
        logging.error(f"Erro ao gerar feedback: {str(e)}")
        # Dica: Se retornar '0' aqui, é o KeyError capturado
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()