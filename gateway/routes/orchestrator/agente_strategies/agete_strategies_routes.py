from flask import Blueprint, request, jsonify
import requests
import logging
import sys
import os
from ...services_routs import STRATEGIES_URL, DOMAIN_URL

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