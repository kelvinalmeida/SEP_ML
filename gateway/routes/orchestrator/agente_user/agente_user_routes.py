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
    Rota reescrita para agregar contexto de estudo:
    1. Notas (Control)
    2. Chats (Strategies)
    3. Metadados de Sessão (Control) -> Domínio (Domain) e Estratégia (Strategies)

    Retorna um JSON estruturado agrupado por Nome do Domínio.
    """

    # 1. Obter Username e Prompt
    try:
        data = request.get_json() or {}
    except:
        return jsonify({"error": "Invalid JSON"}), 400

    user_prompt = data.get('prompt') # O prompt original usava 'prompt' ou 'user_prompt'? Prompt diz "user_prompt" na saída, mas input geralmente é 'prompt' ou 'message'. Vou suportar 'prompt'.
    if not user_prompt:
        # Tenta 'user_prompt' caso o frontend mande assim
        user_prompt = data.get('user_prompt')

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

    # Estrutura final
    study_context = {}

    # Helper para cachear domínios e estratégias para evitar chamadas repetidas na mesma execução
    domain_cache = {}
    strategy_cache = {}

    for session_id, performance_data in grades_history.items():
        try:
            # 3.1 Buscar Metadados da Sessão
            # Control: GET /sessions/<id>
            sess_resp = requests.get(f"{CONTROL_URL}/sessions/{session_id}")
            if sess_resp.status_code != 200:
                continue
            
            session_meta = sess_resp.json()

            # Identificar Domain ID
            # session_meta['domains'] é uma lista de IDs. Pegamos o primeiro.
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
                        "videos": [] # Vamos unificar videos_uploaded e videos_youtube aqui?
                                     # O prompt pede "videos": [{"url": "..."}].
                                     # videos_youtube tem 'url'. videos_uploaded tem 'filename'/'path'.
                                     # Vou formatar para padronizar.
                    },
                    "sessions_history": []
                }

                # Popula videos
                video_list = []
                for v in domain_info.get('videos_youtube', []):
                    video_list.append({"url": v.get('url'), "type": "youtube", "title": v.get('title', 'Video Youtube')})
                for v in domain_info.get('videos_uploaded', []):
                    # Para videos upload, a URL seria algo servido pelo backend, mas aqui mando o path ou filename
                    video_list.append({"url": v.get('filename'), "type": "upload", "title": v.get('filename')})

                study_context[domain_name]["material_complementar"]["videos"] = video_list

            # 3.3 Identificar Estratégia para filtrar chats
            # Prioridade: original_strategy_id > primeiro da lista strategies
            strategy_id = session_meta.get('original_strategy_id')
            if not strategy_id and session_meta.get('strategies'):
                strategy_id = session_meta['strategies'][0]
            
            strategy_id = str(strategy_id) if strategy_id else None

            # 3.4 Buscar Táticas da Estratégia (para filtrar chats)
            session_interactions = []

            if strategy_id:
                if strategy_id in strategy_cache:
                    tactics = strategy_cache[strategy_id]
                else:
                    strat_resp = requests.get(f"{STRATEGIES_URL}/strategies/{strategy_id}")
                    if strat_resp.status_code == 200:
                        strat_data = strat_resp.json()
                        tactics = strat_data.get('tatics', []) # Note a typo 'tatics' no serviço strategies
                        strategy_cache[strategy_id] = tactics
                    else:
                        tactics = []

                # Cria mapa de táticas {id: name}
                tactic_map = {str(t['id']): t['name'] for t in tactics}

                # Cruza com chat_history
                # chat_history é {tactic_id: {general: [], private: []}}
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

    return jsonify(final_payload), 200
