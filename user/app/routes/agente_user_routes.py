import json
import logging
import os
from flask import Blueprint, request, jsonify, current_app
from google import genai
from openai import OpenAI
from config import Config

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
        db_url = getattr(Config, 'SQLALCHEMY_DATABASE_URI', os.getenv('DATABASE_URL'))
        conn = create_connection(db_url)
        
        if not conn:
             return jsonify({"error": "Falha na conexão com o banco de dados"}), 500

        students_data = []
        
        with conn.cursor() as cur:
            try:
                clean_ids = [int(x) for x in student_ids]
            except ValueError:
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

        profiles_text = []
        for s in students_data:
            name = s.get('name', 'Aluno')
            p_type = s.get('pref_content_type') or 'Não informado'
            p_comm = s.get('pref_communication') or 'Não informado'
            recebe_email = s.get('pref_receive_email')
            txt_email = "Aceita receber emails" if recebe_email else "NÃO aceita emails"
            
            profiles_text.append(f"- Aluno {name}: Prefere '{p_type}' via '{p_comm}'. {txt_email}.")
        
        profiles_joined = "\n".join(profiles_text)

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

        client = OpenAI(
            api_key=Config.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Você é um assistente pedagógico conciso."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2 
        )

        content_text = response.choices[0].message.content
        
        try:
            summary_dict = json.loads(content_text)
        except json.JSONDecodeError:
            summary_dict = {
                "resumo": content_text,
                "perfil_turma": {},
                "uso_email": "Indeterminado"
            }

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
    Gera um feedback ou resposta para o aluno baseada no prompt e contexto agregado.
    Adaptação para receber payload agregado do Gateway.
    """
    data = request.get_json() or {}
    conn = None

    try:
        # 1. Extração de Dados do Payload Agregado
        username = data.get('student_username')
        user_prompt = data.get('user_prompt')
        study_context = data.get('study_context', {})

        if not username:
            return jsonify({"error": "student_username é obrigatório"}), 400

        # 2. Conectar ao Banco para buscar Preferências (Perfil do Aluno)
        db_url = getattr(Config, 'SQLALCHEMY_DATABASE_URI', os.getenv('DATABASE_URL'))
        conn = create_connection(db_url)

        prefs = {}
        if conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT pref_content_type, pref_communication, pref_receive_email
                    FROM student WHERE username = %s
                """, (username,))
                row = cur.fetchone()
                if row:
                    prefs = dict(row)

        # 3. Configuração LLM
        if not Config.GROQ_API_KEY:
             return jsonify({"error": "GROQ_API_KEY não configurada"}), 500

        client = OpenAI(
            api_key=Config.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )

        # 4. Construção do Contexto para o Prompt
        context_str = "CONTEXTO DE ESTUDO RECENTE:\n"
        last_session_id = None
        last_domain_name = None

        if not study_context:
            context_str += "Nenhum histórico recente encontrado.\n"
        else:
            for d_name, d_info in study_context.items():
                context_str += f"\n=== Domínio: {d_name} ===\n"
                context_str += f"Descrição: {d_info.get('description', '')}\n"

                # Materiais
                mats = d_info.get('material_complementar', {})
                pdfs = [p.get('filename') for p in mats.get('pdfs', [])]
                videos = [v.get('title') for v in mats.get('videos', [])]
                if pdfs: context_str += f"Materiais PDF: {', '.join(pdfs)}\n"
                if videos: context_str += f"Vídeos: {', '.join(videos)}\n"

                # Sessões
                for sess in d_info.get('sessions_history', []):
                    sess_id = sess.get('session_id')
                    # Guardamos o último ID encontrado para salvar no banco (melhor esforço)
                    last_session_id = sess_id
                    last_domain_name = d_name

                    perf = sess.get('performance', {})
                    context_str += f"-- Sessão {sess_id}: Notas {perf.get('notes')} | Extras {perf.get('extra_notes')}\n"

                    interactions = sess.get('interactions', [])
                    if interactions:
                        context_str += "   Interações (Chat):\n"
                        for inter in interactions:
                            tname = inter.get('tactic_name', 'Tática')
                            msgs = inter.get('messages', {})
                            gen_msgs = msgs.get('general', [])
                            if gen_msgs:
                                context_str += f"     [{tname}] Geral: {gen_msgs}\n"

        # 5. Prompt Final
        system_prompt = f"""
        Você é um Mentor Pedagógico Pessoal e Inteligente.
        O aluno {username} entrou em contato.

        PERFIL DO ALUNO:
        - Prefere conteúdo: {prefs.get('pref_content_type', 'Não informado')}
        - Comunicação: {prefs.get('pref_communication', 'Não informado')}
        - Email: {'Sim' if prefs.get('pref_receive_email') else 'Não'}

        {context_str}

        SUA TAREFA:
        Responda ao PROMPT DO USUÁRIO abaixo.
        1. Se for uma dúvida, responda usando o contexto (se relevante).
        2. Se for um pedido de feedback, analise o desempenho nas sessões listadas.
        3. Adapte a resposta ao perfil do aluno.
        4. Seja encorajador e direto.
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": str(user_prompt)}
            ],
            temperature=0.5,
            max_tokens=600
        )

        feedback_text = response.choices[0].message.content

        # 6. Salvar no Banco (Se tiver conexão e contexto mínimo)
        new_id = None
        if conn and feedback_text:
            try:
                # Se last_session_id for string, tenta converter para int pois o banco espera INT
                sid_to_save = None
                if last_session_id:
                    try:
                        sid_to_save = int(last_session_id)
                    except ValueError:
                        pass

                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO student_feedback
                        (student_username, session_id, domain_name, feedback_content)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                    """, (username, sid_to_save, last_domain_name, feedback_text))

                    new_row = cur.fetchone()
                    if new_row:
                        if isinstance(new_row, dict):
                            new_id = new_row['id']
                        else:
                            new_id = new_row[0]
                    conn.commit()
            except Exception as db_err:
                logging.warning(f"Não foi possível salvar feedback no banco: {db_err}")

        return jsonify({
            "status": "success",
            "student": username,
            "response": feedback_text,
            "feedback_id": new_id
        }), 200

    except Exception as e:
        logging.error(f"Erro ao gerar feedback: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


@agente_user_bp.route('/agent/help_student', methods=['POST'])
def help_student_agent():
    """
    Rota legada/alternativa. Mantida para compatibilidade se necessário.
    """
    # ... (mesma implementação anterior ou redireciona para a nova)
    # Por segurança, mantemos o código original desta função se ele for usado por outros componentes.
    # Vou replicar o código original que estava aqui para não quebrar nada.
    try:
        data = request.get_json()
        username = data.get('student_username')
        user_prompt = data.get('user_prompt')
        profile = data.get('student_profile', {})
        history = data.get('session_history', {})
        
        if not Config.GROQ_API_KEY:
             return jsonify({"error": "GROQ_API_KEY não configurada"}), 500

        client = OpenAI(
            api_key=Config.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )

        context_text = ""
        if history:
            context_text += "HISTÓRICO:\n"
            for sess_id, info in history.items():
                domain = info.get('domain', {})
                grades = info.get('grades', {})
                context_text += f"Sessão {sess_id}: {domain.get('title')} - Notas: {grades.get('notes')}\n"
        
        system_prompt = f"Tutor Inteligente para {username}. Contexto: {context_text}"

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5
        )

        return jsonify({
            "status": "success",
            "response": response.choices[0].message.content
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
