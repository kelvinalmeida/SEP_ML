from flask import Blueprint, request, jsonify
import requests
from requests.exceptions import RequestException
import logging

# Tenta importar as configurações de rotas. 
# Como este arquivo está em uma subpasta profunda (routes/orchestrator/agentes_strategies),
# usamos importação absoluta assumindo que o Python Path começa na raiz do 'gateway'.
try:
    from routes.services_routs import STRATEGIES_URL, DOMAIN_URL
except ImportError:
    # Fallback: Tenta importar subindo os níveis se executado como pacote
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from services_routs import STRATEGIES_URL, DOMAIN_URL

# Criação do Blueprint
agete_strategies_bp = Blueprint('agete_strategies_bp', __name__)

@agete_strategies_bp.route('/strategies/orchestrate_validation', methods=['POST'])
def orchestrate_validation():
    """
    Age como o Agente Orquestrador.
    Função:
    1. Recebe o pedido do Front (Estratégia + Táticas).
    2. Busca 'Memória' no serviço Domain (Contexto pedagógico).
    3. Invoca 'Especialista' no serviço Strategies (Agente Crítico).
    4. Retorna a validação consolidada para o usuário.
    """
    try:
        data = request.json
        strategy_name = data.get('name')
        tactics_names = data.get('tactics', []) # Espera uma lista de nomes de táticas
        article_id = 1 # Definido estático para o MVP (Padrão Pedagógico)
        
        # ---------------------------------------------------------
        # 1. Passo: Buscar Memória (Call Domain Service)
        # ---------------------------------------------------------
        article_content = ""
        try:
            # O Gateway consulta o serviço de Domínio para pegar o contexto do PDF/RAG
            domain_response = requests.get(f"{DOMAIN_URL}/get_content/{article_id}", timeout=5)
            
            if domain_response.status_code == 200:
                article_content = domain_response.json().get('content', "")
            else:
                logging.warning(f"Domain Service retornou erro: {domain_response.status_code}")
                article_content = "Conteúdo padrão de referência pedagógica (Fallback: Domínio indisponível)."

        except Exception as e:
             logging.error(f"Erro ao conectar com Domain: {e}")
             # Não falha o processo todo, apenas segue com contexto limitado
             article_content = "Conteúdo padrão (Erro de conexão com Memória)."

        # ---------------------------------------------------------
        # 2. Passo: Chamar o Agente Worker (Call Strategies Service)
        # ---------------------------------------------------------
        worker_payload = {
            "name": strategy_name,
            "tactics": tactics_names,
            "context": article_content
        }
        
        try:
            # Chama o endpoint do Agente de Estratégia (que deve ser implementado no microsserviço Strategies)
            agent_response = requests.post(f"{STRATEGIES_URL}/agent/critique", json=worker_payload, timeout=10)
            
            if agent_response.status_code == 200:
                return jsonify(agent_response.json())
            else:
                return jsonify({
                    "grade": 0, 
                    "feedback": f"O Agente de Estratégia não conseguiu processar. Status: {agent_response.status_code}", 
                    "status": "error"
                }), agent_response.status_code

        except RequestException as e:
            logging.error(f"Erro ao conectar com Strategies Agent: {e}")
            return jsonify({
                "grade": 0, 
                "feedback": "Erro de comunicação com o Agente Especialista (Strategies).", 
                "status": "error"
            }), 503

    except Exception as e:
        return jsonify({"error": "Orchestration failed", "details": str(e)}), 500