from flask import Blueprint, request, jsonify
import requests
import logging
import sys
import os
from ...services_routs import STRATEGIES_URL, DOMAIN_URL, CONTROL_URL, USER_URL

# Importação robusta das variáveis de serviço (STRATEGIES_URL, DOMAIN_URL)
# Tenta importar relativo, se falhar (devido à profundidade da pasta), ajusta o path.
# try:
#     from routes.services_routs import STRATEGIES_URL, DOMAIN_URL
# except ImportError:
#     # Adiciona o diretório raiz do gateway ao path
#     sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
#     from services_routs import STRATEGIES_URL, DOMAIN_URL

agete_strategies_bp = Blueprint('agete_strategies_bp', __name__)

@agete_strategies_bp.route('/strategies/orchestrate_validation', methods=['POST'])
def orchestrate_validation():
    """
    Agente Orquestrador.
    Fluxo:
    1. Recebe dados do Front.
    2. Busca o conteúdo do Artigo no serviço de Domínio (Memória).
    3. Envia Artigo + Estratégia para o serviço Strategies (Worker com Gemini).
    4. Devolve a resposta para o Front.
    """
    try:
        data = request.json
        strategy_name = data.get('name')
        tactics_names = data.get('tactics', [])
        
        # ID do artigo fixo para este cenário (Padrão Pedagógico)
        article_id = 1 
        
        # ---------------------------------------------------------
        # 1. Passo: Buscar Memória (Call Domain Service)
        # ---------------------------------------------------------
        article_content = ""
        try:
            # O Orquestrador pede ao Domain o texto extraído do PDF
            domain_response = requests.get(f"{DOMAIN_URL}/get_content/1", timeout=10)
            
            if domain_response.status_code == 200:
                article_content = domain_response.json().get('content', "")
                if not article_content:
                    logging.warning("Conteúdo do artigo veio vazio do Domain.")
                    article_content = "Conteúdo não disponível. Avalie apenas com base nas boas práticas gerais."
            else:
                logging.warning(f"Domain Service retornou erro: {domain_response.status_code}")
                article_content = "Erro ao recuperar contexto pedagógico. Avalie genericamente."

        except Exception as e:
             logging.error(f"Erro ao conectar com Domain: {e}")
             article_content = "Sistema de memória indisponível."

        # ---------------------------------------------------------
        # 2. Passo: Chamar o Agente Worker (Call Strategies Service)
        # ---------------------------------------------------------
        worker_payload = {
            "name": strategy_name,
            "tactics": tactics_names,
            "context": article_content
        }

        # logging.warning(f"Payload enviado ao Strategies Agent: {worker_payload}")

        logging.warning(f"Domain Service retornou erro: {domain_response.status_code}")
        
        try:
            # Envia para o serviço Strategies onde o Gemini processará
            agent_response = requests.post(f"{STRATEGIES_URL}/agent/critique", json=worker_payload, timeout=30)
            
            if agent_response.status_code == 200:
                return jsonify(agent_response.json())
            else:
                return jsonify({
                    "grade": 0, 
                    "feedback": f"O Agente de Estratégia falhou. Código: {agent_response.status_code}", 
                    "status": "error"
                }), agent_response.status_code

        except Exception as e:
            logging.error(f"Erro ao conectar com Strategies Agent: {e}")
            return jsonify({
                "grade": 0, 
                "feedback": "Erro de comunicação com o Agente Especialista.", 
                "status": "error"
            }), 503

    except Exception as e:
        return jsonify({"error": "Orchestration failed", "details": str(e)}), 500


@agete_strategies_bp.route('/sessions/<int:session_id>/execute_rules', methods=['POST'])
def execute_rules_logic(session_id):
    """
    Lógica da Tática 'Regras' (Cérebro da Sessão).
    Coleta contexto, consulta o Agente de Estratégia e executa a decisão (Repetir Tática ou Mudar Estratégia).
    """
    try:
        logging.info(f"🧠 Executando Lógica de Regras para Sessão {session_id}")

        # ---------------------------------------------------------
        # 1. Agregação de Contexto (Data Fetching)
        # ---------------------------------------------------------

        # A. Control: Dados da Sessão (para obter strategy_id e histórico de táticas)
        session_res = requests.get(f"{CONTROL_URL}/sessions/{session_id}")
        if session_res.status_code != 200:
             return jsonify({"error": "Falha ao buscar sessão no Control"}), 500
        session_data = session_res.json()

        strategy_id = session_data.get('strategies', [None])[0]
        current_tactic_index = session_data.get('current_tactic_index', 0)

        # Inferir táticas executadas (similar ao execute_agent_logic)
        executed_ids = []
        tactics_list = []
        if strategy_id:
             strat_res = requests.get(f"{STRATEGIES_URL}/strategies/{strategy_id}")
             if strat_res.status_code == 200:
                 tactics_list = strat_res.json().get('tatics', [])
                 # Consideramos executadas todas até o índice atual (inclusive)
                 for i in range(current_tactic_index + 1):
                     if i < len(tactics_list):
                         executed_ids.append(tactics_list[i]['id'])

        # B. Control: Resumo de Desempenho (Agent Summary)
        summary_res = requests.get(f"{CONTROL_URL}/sessions/{session_id}/agent_summary")
        performance_summary = summary_res.json().get('summary', '') if summary_res.status_code == 200 else "Sem dados de performance."

        # C. User: Perfil da Turma
        student_ids = session_data.get('students', [])
        student_profile_summary = "Sem alunos."
        if student_ids:
             user_res = requests.post(f"{USER_URL}/students/summarize_preferences", json={"student_ids": student_ids})
             student_profile_summary = user_res.json().get('summary', '') if user_res.status_code == 200 else "Sem perfil de alunos."

        # D. Domain: Conteúdo da Aula (Fixo ID=2 para MVP)
        domain_res = requests.get(f"{DOMAIN_URL}/get_content/2")
        article_text = domain_res.json().get('content', '') if domain_res.status_code == 200 else "Conteúdo não disponível."

        # ---------------------------------------------------------
        # 2. Consulta ao Oráculo (Decision Making)
        # ---------------------------------------------------------
        payload = {
            "strategy_id": strategy_id,
            "executed_tactics": executed_ids,
            "performance_summary": performance_summary,
            "student_profile_summary": student_profile_summary,
            "article_text": article_text
        }

        logging.info("🔮 Consultando Agente de Regras...")
        agent_res = requests.post(f"{STRATEGIES_URL}/agent/decide_rules_logic", json=payload)

        if agent_res.status_code != 200:
             logging.error(f"Erro no Strategies Service: {agent_res.text}")
             return jsonify({"error": "Strategies service error", "details": agent_res.text}), 502

        decision_data = agent_res.json().get('rule_execution', {})
        decision = decision_data.get('decision')
        target_id = decision_data.get('target_id')
        reasoning = decision_data.get('reasoning')

        logging.info(f"🤖 Decisão: {decision} | Alvo: {target_id} | Motivo: {reasoning}")

        # ---------------------------------------------------------
        # 3. Execução da Ação (Actuation)
        # ---------------------------------------------------------

        # CENÁRIO A: Repetir Tática
        if decision == "REPEAT_TACTIC":
             # Precisamos converter o target_id (ID da tática) para o Índice na estratégia atual
             target_index = -1
             target_tactic_name = "Desconhecida"

             for idx, t in enumerate(tactics_list):
                 if int(t['id']) == int(target_id):
                     target_index = idx
                     target_tactic_name = t['name']
                     break

             if target_index != -1:
                 # Chama Control para pular para a tática (usando set_tactic_index pois control usa índices)
                 requests.post(f"{CONTROL_URL}/sessions/tactic/set/{session_id}", json={'tactic_index': target_index})
                 logging.info(f"✅ Tática repetida: {target_tactic_name} (Index {target_index})")
             else:
                 logging.warning(f"⚠️ Tática alvo ID {target_id} não encontrada na estratégia atual.")
                 return jsonify({"error": "Tática alvo não encontrada na estratégia"}), 404

        # CENÁRIO B: Mudar de Estratégia
        elif decision == "NEXT_STRATEGY":
             # Troca a estratégia da sessão
             requests.post(f"{CONTROL_URL}/sessions/{session_id}/change_strategy", json={'strategy_id': target_id})
             logging.info(f"✅ Estratégia alterada para ID {target_id}")

        return jsonify({
            "success": True,
            "decision": decision,
            "reasoning": reasoning,
            "target_id": target_id
        })

    except Exception as e:
        logging.error(f"Erro fatal em execute_rules_logic: {e}")
        return jsonify({"error": str(e)}), 500
