from flask import Blueprint, request, jsonify
import requests
import logging
import json
import sys
import os
from concurrent.futures import ThreadPoolExecutor
from ...services_routs import STRATEGIES_URL, DOMAIN_URL, CONTROL_URL, USER_URL
from ...auth import token_required

# Importação robusta das variáveis de serviço (STRATEGIES_URL, DOMAIN_URL)
# Tenta importar relativo, se falhar (devido à profundidade da pasta), ajusta o path.
# try:
#     from routes.services_routs import STRATEGIES_URL, DOMAIN_URL
# except ImportError:
#     # Adiciona o diretório raiz do gateway ao path
#     sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
#     from services_routs import STRATEGIES_URL, DOMAIN_URL

agete_user_bp = Blueprint('agete_user_bp', __name__)

import logging

logging.basicConfig(
    level=logging.INFO,  # Set minimum log level required (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s [%(levelname)s] %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S'
)

@agete_user_bp.route('/orchestrator/student/ask_tutor', methods=['POST'])
@token_required
def ask_tutor(current_user):
    """
    Rota que recebe a dúvida do aluno, coleta o contexto de notas e chats (Control e Strategies)
    organizado por sessão e envia para o Agente User (que buscará o perfil localmente) gerar uma resposta.
    """

    try:
        # 1. Obter o Prompt do Aluno
        data = request.get_json()
        user_prompt = data.get('prompt')
        
        if not user_prompt:
            return jsonify({"error": "O campo 'prompt' é obrigatório."}), 400

        # O username vem do token
        username = current_user.get('username') if isinstance(current_user, dict) else current_user

        # ------------------------------------------------------------------
        # 2. Coleta de Dados Paralela (Control e Strategies apenas)
        # ------------------------------------------------------------------
        # Removemos o fetch_profile daqui. O Agente User fará isso internamente.
        
        def fetch_grades():
            # Busca notas no Control Service
            try:
                resp = requests.get(f"{CONTROL_URL}/students/{username}/grades_history")
                return resp.json() if resp.status_code == 200 else {}
            except: return {}

        def fetch_chats():
            # Busca chats no Strategies Service
            try:
                resp = requests.get(f"{STRATEGIES_URL}/students/{username}/chat_history")
                return resp.json() if resp.status_code == 200 else {}
            except: return {}

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_grades = executor.submit(fetch_grades)
            future_chats = executor.submit(fetch_chats)

            grades_history = future_grades.result()
            chat_history = future_chats.result()
        
        # ------------------------------------------------------------------
        # 3. Consolidação dos Dados (Organizar por Sessão)
        # ------------------------------------------------------------------
        consolidated_sessions = {}
        
        # Iteramos sobre as sessões encontradas no histórico de notas
        for session_id, grades_data in grades_history.items():
            
            # 3.1 Inicializa estrutura da sessão
            consolidated_sessions[session_id] = {
                "grades": grades_data,
                "domain": {},
                "chats": []
            }

            # 3.2 Buscar Metadados da Sessão (Control) para pegar Domain ID e Tactics
            try:
                sess_resp = requests.get(f"{CONTROL_URL}/sessions/{session_id}")
                if sess_resp.status_code == 200:
                    sess_meta = sess_resp.json()
                    
                    # 3.3 Buscar Domínio (Domain Service)
                    domain_id = sess_meta.get('domain_id')
                    if domain_id:
                        dom_resp = requests.get(f"{DOMAIN_URL}/get_content/{domain_id}")
                        if dom_resp.status_code == 200:
                            consolidated_sessions[session_id]["domain"] = dom_resp.json()

                    # 3.4 Vincular Chats a esta Sessão
                    current_strategy_id = sess_meta.get('original_strategy_id')
                    
                    # Busca táticas da estratégia (Strategies Service)
                    tactics_resp = requests.get(f"{STRATEGIES_URL}/strategies/{current_strategy_id}/tactics")
                    if tactics_resp.status_code == 200:
                        session_tactics = tactics_resp.json()
                        session_tactic_ids = [str(t['id']) for t in session_tactics]
                        
                        # Filtra o chat_history: Se o chat foi numa tática desta sessão, adiciona.
                        for tid, chat_data in chat_history.items():
                            if tid in session_tactic_ids:
                                consolidated_sessions[session_id]["chats"].append({
                                    "tactic_id": tid,
                                    "data": chat_data
                                })
            
            except Exception as e:
                logging.error(f"Erro ao consolidar sessão {session_id}: {e}")

        # ------------------------------------------------------------------
        # 4. Montagem do Payload Final para o Agente User
        # ------------------------------------------------------------------
        agent_payload = {
            "student_username": username,
            # "student_profile": REMOVIDO (O User Service buscará no próprio DB)
            "user_prompt": user_prompt,
            "session_history": consolidated_sessions,
            "raw_chat_history": chat_history 
        }

        return f"Payload enviado ao Agente User para {agent_payload}."

        logging.info(f"Payload enviado ao Agente User para {agent_payload}...")

        # ------------------------------------------------------------------
        # 5. Enviar para o Serviço User (Agente)
        # ------------------------------------------------------------------
        agent_response = requests.post(
            f"{USER_URL}/agent/help_student", 
            json=agent_payload,
            timeout=60
        )

        if agent_response.status_code == 200:
            return jsonify(agent_response.json()), 200
        else:
            return jsonify({
                "error": "O Agente User não conseguiu processar a solicitação.",
                "details": agent_response.text
            }), agent_response.status_code

    except Exception as e:
        logging.error(f"Erro crítico no orquestrador do aluno: {str(e)}")
        return jsonify({"error": str(e)}), 500