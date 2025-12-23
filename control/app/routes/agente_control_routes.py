import logging
import os
from flask import Blueprint, request, jsonify, current_app
from google import genai
from config import Config

# Tenta importar a conexão do banco de dados
try:
    from db import create_connection
except ImportError:
    from ...db import create_connection

agente_control_bp = Blueprint('agente_control_bp', __name__)

# ... (Mantenha suas outras rotas existentes: create_session, etc.) ...

# ==============================================================================
# AGENTE DE MEMÓRIA (CONTROL): RESUMO GERAL DA SESSÃO (Foco na Turma/Estratégia)
# ==============================================================================
@agente_control_bp.route('/sessions/<int:session_id>/agent_summary', methods=['GET'])
def agent_session_summary(session_id):
    """
    Agente Control: Analisa os dados macro da sessão.
    Foco: Desempenho geral, adesão às atividades extras e status do plano de aula.
    Não analisa alunos individualmente.
    """
    conn = None
    try:
        # 1. Conexão
        db_url = current_app.config.get("SQLALCHEMY_DATABASE_URI") or os.getenv("DATABASE_URL")
        conn = create_connection(db_url)
        
        if not conn:
            return jsonify({"error": "Falha na conexão com o banco de dados"}), 500

        with conn.cursor() as cur:
            # A. Dados da Sessão
            cur.execute("""
                SELECT status, start_time, current_tactic_index 
                FROM session 
                WHERE id = %s
            """, (session_id,))
            session_info = cur.fetchone()

            if not session_info:
                return jsonify({"error": "Sessão não encontrada"}), 404

            # B. Total de Estratégias no Plano
            cur.execute("""
                SELECT COUNT(*) as total 
                FROM session_strategies 
                WHERE session_id = %s
            """, (session_id,))
            total_strategies = cur.fetchone()['total']

            # C. Notas dos Exercícios (Lista de inteiros)
            # Pegamos apenas os scores para análise estatística
            cur.execute("""
                SELECT score 
                FROM verified_answers 
                WHERE session_id = %s
            """, (session_id,))
            exercise_rows = cur.fetchall()
            # Ex: [10, 5, 8, 9]
            exercise_scores = [row['score'] for row in exercise_rows]

            # D. Notas Extras (Lista de floats)
            cur.execute("""
                SELECT extra_notes 
                FROM extra_notes 
                WHERE session_id = %s
            """, (session_id,))
            extra_rows = cur.fetchall()
            # Ex: [9.5, 8.0]
            extra_scores = [row['extra_notes'] for row in extra_rows]

        # 2. Estatísticas Gerais (Cálculos Python)
        total_exercises = len(exercise_scores)
        avg_exercises = sum(exercise_scores) / total_exercises if total_exercises > 0 else 0
        
        total_extras = len(extra_scores)
        avg_extras = sum(extra_scores) / total_extras if total_extras > 0 else 0

        # 3. Engenharia de Prompt (Foco no Coletivo)
        # Passamos as listas de notas para ele detectar padrões (ex: turma homogênea vs heterogênea)
        prompt = f"""
        Atue como o 'Agente de Memória' de uma plataforma de ensino.
        Analise o estado geral desta Sessão de Ensino (ID {session_id}) para orientar o Orquestrador.
        Não cite alunos. Foque na eficácia das estratégias e no desempenho da turma como um todo.

        DADOS DA SESSÃO:
        - Status: {session_info['status']}
        - Progresso do Plano: {total_strategies} estratégias vinculadas.
        
        DESEMPENHO NOS EXERCÍCIOS OBRIGATÓRIOS:
        - Quantidade de respostas: {total_exercises}
        - Média Geral: {avg_exercises:.1f} / 10
        - Distribuição das Notas: {exercise_scores}
        
        DESEMPENHO NAS ATIVIDADES EXTRAS (BÔNUS):
        - Quantidade de entregas: {total_extras}
        - Média Geral: {avg_extras:.1f}
        - Notas: {extra_scores}

        OBJETIVO:
        Gere um resumo narrativo curto (2-3 frases) respondendo:
        1. O conteúdo obrigatório está sendo bem assimilado pela maioria?
        2. Existe interesse/adesão ao conteúdo extra?
        3. A sessão parece fluir bem ou está estagnada (poucas respostas)?
        """

        # 4. Chamada ao Gemini
        if not Config.GEMINI_API_KEY:
             return jsonify({"error": "GEMINI_API_KEY não configurada"}), 500

        client = genai.Client(api_key=Config.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )

        # 5. Retorno
        return jsonify({
            "session_id": session_id,
            "status": session_info['status'],
            "summary": response.text.strip(),
            "metrics": {
                "exercise_avg": round(avg_exercises, 2),
                "extra_avg": round(avg_extras, 2),
                "participation_count": total_exercises + total_extras
            }
        }), 200

    except Exception as e:
        logging.error(f"Erro no Agente Control Summary: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()