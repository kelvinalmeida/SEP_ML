import os
import json
import logging
from flask import Blueprint, request, jsonify, current_app
from google import genai
from google.genai import types

agente_strategies_bp = Blueprint('agente_strategies_bp', __name__)

# Configuração da API Key
# Tenta pegar do ambiente (Docker env), ou usa a chave direta como fallback
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 


@agente_strategies_bp.route('/agent/critique', methods=['POST'])
def critique_strategy():
    """
    Agente Worker: Crítico Pedagógico (Versão Google GenAI SDK v1)
    """
    try:
        # 1. Extração de dados
        data = request.json
        strategy_name = data.get('name')
        tactics_list = data.get('tactics', [])
        reference_article = data.get('context')

        # 2. Configuração do Cliente (Nova SDK)
        client = genai.Client(api_key=GEMINI_API_KEY)

        # 3. Construção do Prompt
        prompt = f"""
        Atue como um Especialista Pedagógico.
        Analise a seguinte estratégia de ensino com base no texto de referência.

        TEXTO DE REFERÊNCIA:
        {reference_article}

        ESTRATÉGIA DO PROFESSOR:
        Nome: {strategy_name}
        Táticas: {', '.join(tactics_list)}

        SAÍDA ESPERADA (JSON):
        {{
            "grade": <nota inteira 0-10>,
            "feedback": "<explicação concisa>"
        }}
        """

        # 4. Chamada ao Modelo
        # Usando response_mime_type para forçar JSON (funcionalidade do Gemini 1.5+)
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        ) 

        logging.info(f"****************Resposta do Agente Gemini: {response.text}")

        # 5. Tratamento da Resposta
        # A nova SDK retorna o texto limpo, e como pedimos JSON, podemos fazer o parse direto
        ai_response = json.loads(response.text)
        
        final_score = ai_response.get('grade', 0)
        final_feedback = ai_response.get('feedback', 'Sem feedback gerado.')
        status = "approved" if final_score >= 7 else "needs_revision"

        return jsonify({
            "grade": final_score,
            "feedback": final_feedback,
            "status": status
        })

    except Exception as e:
        logging.error(f"Erro no Agente Gemini: {str(e)}")
        return jsonify({
            "grade": 0, 
            "feedback": f"Erro interno na IA: {str(e)}",
            "status": "error"
        }), 500