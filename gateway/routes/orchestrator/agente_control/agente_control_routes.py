
import requests
import logging
import re
from flask import jsonify
from ...services_routs import CONTROL_URL, STRATEGIES_URL, USER_URL, DOMAIN_URL

def execute_agent_logic(session_id, session_json):
    """
    Executa a lógica do Agente de Estratégia:
    1. Agrega dados (Contexto, Perfil, Performance).
    2. Consulta o Agente.
    3. Aplica a decisão.
    """
    try:
        # === FLUXO DE AGENTE DE IA ===
        logging.info("🤖 Agente de Estratégia ATIVADO. Iniciando ciclo de decisão...")

        # 1. Dados da Sessão (Control)
        strategy_id = session_json.get('strategies', [None])[0]

        # Inferir táticas executadas
        executed_ids = []
        if strategy_id:
            strat_res = requests.get(f"{STRATEGIES_URL}/strategies/{strategy_id}")
            if strat_res.status_code == 200:
                # strat_data = strat_res.json()
                # tactics = strat_data.get('tatics', [])
                # current_idx = session_json.get('current_tactic_index', 0)
                # Inclui a atual que está terminando
                # for i in range(current_idx + 1):
                #      if i < len(tactics):
                #          executed_ids.append(tactics[i]['id'])

                # CORREÇÃO: Não inferir execução completa baseada no índice (0..current).
                # Problema 1: Se o agente pula táticas, as anteriores ficam marcadas como 'executadas' e ele não as escolhe.
                # Problema 2: Se enviarmos lista vazia [], ele não sabe o que ACABOU de fazer e entra em loop repetindo a mesma.
                # Solução Paliativa: Enviar APENAS a tática atual (que acabou de finalizar) como executada.
                # Isso previne o loop imediato e permite escolher qualquer outra (anteriores ou futuras).

                executed_ids = []
                current_idx = session_json.get('current_tactic_index', 0)

                if 0 <= current_idx < len(tactics):
                    # Adiciona apenas a tática atual à lista de executadas
                    executed_ids.append(tactics[current_idx]['id'])

        performance_res = requests.get(f"{CONTROL_URL}/sessions/{session_id}/agent_summary")
        performance_summary = performance_res.json().get('summary', 'Sem dados de performance.') if performance_res.status_code == 200 else 'Erro ao buscar performance.'

        # 2. Dados do Aluno/Turma (User)
        student_ids = session_json.get('students', [])
        student_profile_summary = "Sem alunos."
        if student_ids:
             user_res = requests.post(f"{USER_URL}/students/summarize_preferences", json={"student_ids": student_ids})
             if user_res.status_code == 200:
                 student_profile_summary = user_res.json().get('summary', 'Perfil não informado.')

        # 3. Conteúdo do Domínio (Domain)
        domain_id = session_json.get('domains', [None])[0]
        domain_name = "Domínio Desconhecido"
        domain_description = ""

        if domain_id:
             dom_res = requests.get(f"{DOMAIN_URL}/domains/{domain_id}")
             if dom_res.status_code == 200:
                 d_data = dom_res.json()
                 domain_name = d_data.get('name', '')
                 domain_description = d_data.get('description', '')

        content_res = requests.get(f"{DOMAIN_URL}/get_content/2") # MVP
        article_text = content_res.json().get('content', '') if content_res.status_code == 200 else ''

        # 4. Chamada ao Agente (Strategies)
        agent_payload = {
            "strategy_id": strategy_id,
            "executed_tactics": executed_ids,
            "student_profile_summary": student_profile_summary,
            "performance_summary": performance_summary,
            "domain_name": domain_name,
            "domain_description": domain_description,
            "article_text": article_text
        }

        logging.info(f"📤 Enviando payload para Agente: {agent_payload.keys()}")
        agent_res = requests.post(f"{STRATEGIES_URL}/agent/decide_next_tactic", json=agent_payload)

        if agent_res.status_code == 200:
            decision = agent_res.json().get('decision', {})
            chosen_tactic_id = decision.get('chosen_tactic_id')

            logging.info(f"📥 Decisão do Agente: Tática ID {chosen_tactic_id}")

            # 5. Aplicar Decisão (Encontrar índice e setar)
            if chosen_tactic_id and strategy_id:
                 strat_res = requests.get(f"{STRATEGIES_URL}/strategies/{strategy_id}")
                 if strat_res.status_code == 200:
                     tactics = strat_res.json().get('tatics', [])
                     target_index = -1
                     for idx, t in enumerate(tactics):
                         if t['id'] == chosen_tactic_id:
                             target_index = idx
                             break

                     if target_index != -1:
                         # Seta o índice no Control
                         requests.post(f"{CONTROL_URL}/sessions/tactic/set/{session_id}", json={'tactic_index': target_index})
                         logging.info(f"✅ Índice da tática atualizado para {target_index}")

                         # --- VERIFICAÇÃO DE MUDANÇA DE ESTRATÉGIA ---
                         current_tactic = tactics[target_index]
                         tactic_name = current_tactic.get('name', '').strip().lower()
                         valid_names = ["mudanca de estrategia", "mudança de estratégia", "mudança de estrategia", "mudanca de estratégia"]

                         if tactic_name in valid_names:
                             description = str(current_tactic.get('description', ''))
                             match = re.search(r'\d+', description)

                             if match:
                                 target_strategy_id = int(match.group())
                                 logging.info(f"🔄 Agente escolheu MUDANÇA DE ESTRATÉGIA para ID: {target_strategy_id}")

                                 # Aciona a troca temporária
                                 switch_res = requests.post(
                                     f"{CONTROL_URL}/sessions/{session_id}/temp_switch_strategy",
                                     json={'strategy_id': target_strategy_id}
                                 )

                                 if switch_res.status_code != 200:
                                     logging.error(f"❌ Falha ao trocar estratégia (Agente): {switch_res.text}")
                                 else:
                                     logging.info("✅ Estratégia trocada com sucesso pelo Agente.")
                             else:
                                 logging.warning(f"⚠️ Tática de mudança escolhida, mas sem ID na descrição: {description}")

                         return jsonify({"success": True, "agent_decision": decision}), 200
                     else:
                         logging.error("❌ Tática escolhida pelo agente não encontrada na estratégia atual.")
        else:
             logging.error(f"❌ Falha no Agente Strategies: {agent_res.text}")

    except Exception as e:
        logging.error(f"Erro na orquestração do Agente: {e}")

    # Se falhar ou não decidir, retorna None para indicar fallback
    return None
