import os
import json
import logging
import google.generativeai as genai
from flask import Blueprint, request, jsonify

agente_strategies_bp = Blueprint('agente_strategies_bp', __name__)

# Configuração da API Key do Gemini
# NOTA: Em produção, mantenha isso em variáveis de ambiente (os.getenv)
GEMINI_API_KEY = "AIzaSyAGbueFa52t4bb0LC-ZLIGyLu-LffPs_gY"
genai.configure(api_key=GEMINI_API_KEY)

@agente_strategies_bp.route('/agent/critique', methods=['POST'])
def critique_strategy():
    """
    Agente Worker que atua como um Crítico Pedagógico usando LLM (Gemini).
    Recebe: A estratégia do usuário e o Contexto (Artigo).
    Retorna: Uma crítica (Nota e Feedback).
    """
    try:
        data = request.json
        strategy_name = data.get('name')
        tactics_list = data.get('tactics', []) # Lista de nomes das táticas
        reference_article = data.get('context') # O texto vindo do Domain

        # 1. Configuração do Modelo
        model = genai.GenerativeModel('gemini-1.5-flash')

        # 2. Construção do Prompt
        prompt = f"""
        Você é um Especialista Pedagógico Sênior e crítico rigoroso.
        
        CONTEXTO DE REFERÊNCIA (Base do conhecimento):
        {reference_article}
        
        ESTRATÉGIA DO PROFESSOR:
        Nome: {strategy_name}
        Táticas escolhidas: {', '.join(tactics_list)}
        
        TAREFA:
        Analise se as táticas escolhidas pelo professor estão alinhadas com o CONTEXTO DE REFERÊNCIA.
        Verifique se o método é adequado para o objetivo educacional implícito no texto.
        
        SAÍDA OBRIGATÓRIA (JSON puro, sem markdown):
        {{
            "grade": <inteiro de 0 a 10>,
            "feedback": "<texto explicativo curto e direto em português>"
        }}
        """

        # 3. Chamada ao Gemini
        response = model.generate_content(prompt)
        
        # 4. Tratamento da Resposta (Limpeza de Markdown se houver)
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        # 5. Parsing do JSON gerado pela IA
        ai_evaluation = json.loads(response_text)
        
        final_score = ai_evaluation.get('grade', 0)
        final_feedback = ai_evaluation.get('feedback', 'Sem feedback gerado.')
        
        # Ajuste de status baseado na nota
        status = "approved" if final_score >= 7 else "needs_revision"

        return jsonify({
            "grade": final_score,
            "feedback": final_feedback,
            "status": status
        })

    except Exception as e:
        logging.error(f"Erro no Agente Gemini: {str(e)}")
        # Fallback caso a IA falhe
        return jsonify({
            "grade": 0, 
            "feedback": "Erro ao processar a crítica com a IA. Tente novamente.",
            "status": "error",
            "details": str(e)
        }), 500