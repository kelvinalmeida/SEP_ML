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


@agete_strategies_bp.route('/strategies/execute_rules_logic/<int:session_id>', methods=['POST'])
def execute_rules_logic(session_id):
    """
    Orquestrador da Tática de Regras.
    Coleta contexto, decide via Agente Strategies e atua no Control.
    """
    try:
        logging.info(f"🔄 Executando Tática de Regras para Sessão {session_id}")

        # ---------------------------------------------------------
        # 1. Agregação de Contexto (Data Fetching)
        # ---------------------------------------------------------

        # A. Busca dados básicos da sessão para obter IDs (Control)
        session_res = requests.get(f"{CONTROL_URL}/sessions/{session_id}")
        if session_res.status_code != 200:
             return jsonify({"error": "Sessão não encontrada no Control."}), 404
        session_data = session_res.json()

        strategy_id = session_data.get('strategies', [None])[0]
        student_ids = session_data.get('students', [])
        current_tactic_index = session_data.get('current_tactic_index', 0)

        if not strategy_id:
             return jsonify({"error": "Sessão sem estratégia definida."}), 400

        # B. Busca dados da Estratégia e histórico
        # Prioriza agent_summary se disponível (conforme solicitação), senão fallback para cálculo linear.
        executed_tactics = []
        strat_data = None

        # C. Busca Performance Summary (Control)
        performance_summary = "Sem dados."
        try:
            perf_res = requests.get(f"{CONTROL_URL}/sessions/{session_id}/agent_summary")
            if perf_res.status_code == 200:
                perf_json = perf_res.json()
                performance_summary = perf_json.get('summary', "Sem resumo disponível.")
                # Tenta pegar executed_tactics do resumo se existir (compatibilidade com futuras versões do Control)
                if 'executed_tactics' in perf_json:
                    executed_tactics = perf_json['executed_tactics']
        except Exception as e:
            logging.error(f"Erro ao buscar agent_summary: {e}")

        # Fallback se executed_tactics não veio do Control
        if not executed_tactics:
            try:
                strat_res = requests.get(f"{STRATEGIES_URL}/strategies/{strategy_id}")
                if strat_res.status_code == 200:
                    strat_data = strat_res.json()
                    all_tactics = strat_data.get('tatics', []) # Note typos in service 'tatics'
                    # Assumindo progressão linear por falta de histórico detalhado no DB atual
                    for i in range(min(current_tactic_index + 1, len(all_tactics))):
                        executed_tactics.append(all_tactics[i]['id'])
                else:
                    logging.warning(f"Erro ao buscar estratégia {strategy_id}")
            except Exception as e:
                logging.error(f"Erro de conexão com Strategies: {e}")


        # D. Busca Perfil da Turma (User)
        student_profile_summary = "Sem perfil."
        if student_ids:
            try:
                user_res = requests.post(f"{USER_URL}/students/summarize_preferences", json={"student_ids": student_ids})
                if user_res.status_code == 200:
                    student_profile_summary = user_res.json().get('summary', "Perfil não retornado.")
            except Exception as e:
                 logging.error(f"Erro ao buscar perfil de alunos: {e}")

        # E. Busca Conteúdo do Domínio (Domain) - MVP id=2
        article_text = ""
        try:
            dom_res = requests.get(f"{DOMAIN_URL}/get_content/2")
            if dom_res.status_code == 200:
                article_text = dom_res.json().get('content', "")
        except Exception as e:
            logging.error(f"Erro ao buscar conteúdo do domínio: {e}")


        # ---------------------------------------------------------
        # 2. Consulta ao Oráculo (Decision Making)
        # ---------------------------------------------------------
        payload = {
            "strategy_id": strategy_id,
            "executed_tactics": executed_tactics,
            "performance_summary": performance_summary,
            "student_profile_summary": student_profile_summary,
            "article_text": article_text
        }

        logging.info("🧠 Consultando Agente de Regras...")
        agent_res = requests.post(f"{STRATEGIES_URL}/agent/decide_rules_logic", json=payload)

        decision_data = {}
        if agent_res.status_code == 200:
            decision_data = agent_res.json()
        else:
            logging.error(f"Falha no Agente Strategies: {agent_res.status_code}")
            return jsonify({"error": "Falha na decisão do agente.", "details": agent_res.text}), 500

        decision = decision_data.get('decision')
        target_id = decision_data.get('target_id')
        reasoning = decision_data.get('reasoning', 'Sem justificativa.')

        logging.info(f"🤖 Decisão: {decision} -> Target: {target_id}")

        # ---------------------------------------------------------
        # 3. Execução da Ação (Actuation)
        # ---------------------------------------------------------

        if decision == "REPEAT_TACTIC":
            if target_id:
                # Se ainda não temos os dados da estratégia (veio do fallback ou não), buscamos agora
                if not strat_data:
                     strat_res = requests.get(f"{STRATEGIES_URL}/strategies/{strategy_id}")
                     if strat_res.status_code == 200:
                         strat_data = strat_res.json()

                target_index = -1
                if strat_data:
                    tactics = strat_data.get('tatics', [])
                    for idx, t in enumerate(tactics):
                        if str(t['id']) == str(target_id):
                            target_index = idx
                            break

                if target_index >= 0:
                    # Usando set_tactic_index pois jump_to_tactic não existe nativamente no Control conforme verificado
                    act_res = requests.post(f"{CONTROL_URL}/sessions/tactic/set/{session_id}", json={"tactic_index": target_index})
                    if act_res.status_code != 200:
                        logging.error("Falha ao pular tática no Control.")
                else:
                    logging.error(f"Tática alvo {target_id} não encontrada na estratégia.")

        elif decision == "NEXT_STRATEGY":
            if target_id:
                act_res = requests.post(f"{CONTROL_URL}/sessions/{session_id}/change_strategy", json={"strategy_id": target_id})
                if act_res.status_code != 200:
                        logging.error("Falha ao mudar estratégia no Control.")

        return jsonify({
            "status": "success",
            "decision": decision,
            "target_id": target_id,
            "reasoning": reasoning
        })

    except Exception as e:
        logging.error(f"Erro crítico em execute_rules_logic: {e}")
        return jsonify({"error": str(e)}), 500
