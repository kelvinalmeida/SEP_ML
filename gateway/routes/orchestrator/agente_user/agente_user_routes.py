from flask import Blueprint, request, jsonify
import requests
import logging
from concurrent.futures import ThreadPoolExecutor
from ...services_routs import STRATEGIES_URL, DOMAIN_URL, CONTROL_URL, USER_URL
from ...auth import token_required

agete_user_bp = Blueprint('agete_user_bp', __name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

@agete_user_bp.route('/orchestrator/student/ask_tutor', methods=['POST'])
@token_required
def ask_tutor(current_user):
    """
    Rota reescrita para agregar contexto de estudo e consultar o Agente User.
    1. Coleta Notas (Control) e Chats (Strategies) em paralelo.
    2. Agrega Metadados de Sessão, Domínio e Táticas.
    3. Envia Payload consolidado para o serviço User (/agent/generate_student_feedback).
    """

    # 1. Obter Username e Prompt
    try:
        data = request.get_json() or {}
    except:
        return jsonify({"error": "Invalid JSON"}), 400

    user_prompt = data.get('prompt') or data.get('user_prompt')

    if not user_prompt:
        return jsonify({"error": "O campo 'prompt' é obrigatório."}), 400

    username = current_user.get('username') if isinstance(current_user, dict) else current_user

    # ------------------------------------------------------------------
    # 2. Coleta de Dados Paralela (Históricos Iniciais)
    # ------------------------------------------------------------------

    def fetch_grades():
        try:
            resp = requests.get(f"{CONTROL_URL}/students/{username}/grades_history")
            return resp.json() if resp.status_code == 200 else {}
        except Exception as e:
            logging.error(f"Erro ao buscar grades: {e}")
            return {}

    def fetch_chats():
        try:
            resp = requests.get(f"{STRATEGIES_URL}/students/{username}/chat_history")
            return resp.json() if resp.status_code == 200 else {}
        except Exception as e:
            logging.error(f"Erro ao buscar chats: {e}")
            return {}

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_grades = executor.submit(fetch_grades)
        future_chats = executor.submit(fetch_chats)
        
        grades_history = future_grades.result()
        chat_history = future_chats.result()

    # ------------------------------------------------------------------
    # 3. Processamento e Agregação
    # ------------------------------------------------------------------

    study_context = {}
    domain_cache = {}
    strategy_cache = {}

    for session_id, performance_data in grades_history.items():
        try:
            # 3.1 Buscar Metadados da Sessão
            sess_resp = requests.get(f"{CONTROL_URL}/sessions/{session_id}")
            if sess_resp.status_code != 200:
                continue
            
            session_meta = sess_resp.json()

            # Identificar Domain ID
            domain_ids = session_meta.get('domains', [])
            domain_id = str(domain_ids[0]) if domain_ids else None

            if not domain_id:
                continue

            # 3.2 Buscar Detalhes do Domínio (com Cache)
            if domain_id in domain_cache:
                domain_info = domain_cache[domain_id]
            else:
                dom_resp = requests.get(f"{DOMAIN_URL}/domains/{domain_id}")
                if dom_resp.status_code == 200:
                    domain_info = dom_resp.json()
                    domain_cache[domain_id] = domain_info
                else:
                    domain_info = {"name": "Domínio Desconhecido", "description": "", "pdfs": [], "videos_uploaded": [], "videos_youtube": []}

            domain_name = domain_info.get('name', 'Domínio Sem Nome')

            # Inicializa grupo do domínio se não existir
            if domain_name not in study_context:
                study_context[domain_name] = {
                    "description": domain_info.get('description', ''),
                    "material_complementar": {
                        "pdfs": domain_info.get('pdfs', []),
                        "videos": []
                    },
                    "sessions_history": []
                }

                # Popula videos
                video_list = []
                for v in domain_info.get('videos_youtube', []):
                    video_list.append({"url": v.get('url'), "type": "youtube", "title": v.get('title', 'Video Youtube')})
                for v in domain_info.get('videos_uploaded', []):
                    video_list.append({"url": v.get('filename'), "type": "upload", "title": v.get('filename')})

                study_context[domain_name]["material_complementar"]["videos"] = video_list

            # 3.3 Identificar Estratégia
            strategy_id = session_meta.get('original_strategy_id')
            if not strategy_id and session_meta.get('strategies'):
                strategy_id = session_meta['strategies'][0]
            
            strategy_id = str(strategy_id) if strategy_id else None

            # 3.4 Buscar Táticas e Filtrar Chats
            session_interactions = []

            if strategy_id:
                if strategy_id in strategy_cache:
                    tactics = strategy_cache[strategy_id]
                else:
                    strat_resp = requests.get(f"{STRATEGIES_URL}/strategies/{strategy_id}")
                    if strat_resp.status_code == 200:
                        strat_data = strat_resp.json()
                        # 'tatics' is a known typo in the strategies service response
                        tactics = strat_data.get('tatics', [])
                        strategy_cache[strategy_id] = tactics
                    else:
                        tactics = []

                tactic_map = {str(t['id']): t['name'] for t in tactics}

                for chat_tactic_id, chat_msgs in chat_history.items():
                    if str(chat_tactic_id) in tactic_map:
                        session_interactions.append({
                            "tactic_id": str(chat_tactic_id),
                            "tactic_name": tactic_map[str(chat_tactic_id)],
                            "messages": chat_msgs
                        })

            # 3.5 Montar Objeto da Sessão
            session_obj = {
                "session_id": str(session_id),
                "performance": {
                    "notes": performance_data.get('notes', []),
                    "extra_notes": performance_data.get('extra_notes', [])
                },
                "interactions": session_interactions
            }

            study_context[domain_name]["sessions_history"].append(session_obj)

        except Exception as e:
            logging.error(f"Erro ao processar sessão {session_id}: {e}")
            continue

    # 4. Montar Payload Final
    final_payload = {
        "student_username": username,
        "user_prompt": user_prompt,
        "study_context": study_context
    }

    # ------------------------------------------------------------------
    # 5. Enviar para Agente User (Serviço Externo)
    # ------------------------------------------------------------------
    try:
        logging.info(f"Enviando payload para User Service: {USER_URL}/agent/generate_student_feedback")
        agent_resp = requests.post(
            f"{USER_URL}/agent/generate_student_feedback",
            json=final_payload,
            timeout=60
        )

        if agent_resp.status_code == 200:
            return jsonify(agent_resp.json()), 200
        else:
            return jsonify({
                "error": "Erro no serviço de Agente User",
                "details": agent_resp.text
            }), agent_resp.status_code

    except requests.exceptions.RequestException as e:
        logging.error(f"Falha ao contatar Agente User: {e}")
        return jsonify({"error": "Falha na comunicação com o Agente User"}), 503
