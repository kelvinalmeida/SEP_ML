import os
import json
import logging
from flask import Blueprint, request, jsonify, current_app
from config import Config
from openai import OpenAI
from google import genai
from google.genai import types

agente_strategies_bp = Blueprint('agente_strategies_bp', __name__)

# Configuração da API Key
# Tenta pegar do ambiente (Docker env), ou usa a chave direta como fallback
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 


# Tenta importar a conexão do banco
try:
    from db import create_connection
except ImportError:
    from ...db import create_connection


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
            model="gemini-2.5-flash-lite-preview-09-2025", 
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
    


@agente_strategies_bp.route('/agent/decide_next_tactic', methods=['POST'])
def decide_next_tactic():
    """
    Agente de Estratégia: Recebe o contexto e o histórico.
    Agora traduz os IDs do histórico para NOMES antes de enviar ao LLM.
    """
    data = request.get_json()

    # --- 1. Extração do Contexto ---
    strategy_id = data.get('strategy_id') # estrategia da sessão para consultar táticas disponíveis
    executed_ids = data.get('executed_tactics', []) # Ex: [1, 2], IDs das tatocas já feitos na sessão
    
    student_profile_summary = data.get('student_profile_summary', 'Perfil não informado.')
    performance_summary = data.get('performance_summary', 'Sem dados de performance.')
    
    domain_name = data.get('domain_name', 'Tópico Geral')
    domain_description = data.get('domain_description', '')
    article_text = data.get('article_text', '')

    if not strategy_id:
        return jsonify({"error": "strategy_id é obrigatório"}), 400

    conn = None
    try:
        db_url = current_app.config.get("SQLALCHEMY_DATABASE_URI") or os.getenv("DATABASE_URL")
        conn = create_connection(db_url)
        
        if not conn:
            return jsonify({"error": "Falha na conexão com o banco"}), 500

        with conn.cursor() as cur:
            # --- 2. Busca Táticas DISPONÍVEIS (Opções) ---
            cur.execute("""
                SELECT id, name, description, time 
                FROM tactics 
                WHERE strategy_id = %s
            """, (int(strategy_id),))
            available_rows = cur.fetchall()

            available_tactics = []
            for row in available_rows:
                # Normalização de acesso (Dict ou Tupla)
                if isinstance(row, dict):
                    t = row
                else:
                    t = {'id': row[0], 'name': row[1], 'description': row[2], 'time': row[3]}
                
                available_tactics.append(t)

            # --- 3. Busca Nomes das Táticas JÁ EXECUTADAS (Histórico) ---
            # O Gemini precisa saber que o ID 1 é "Vídeo" para não repetir "Vídeo"
            executed_names_list = []
            
            if executed_ids:
                # Query para pegar nomes baseados nos IDs recebidos
                cur.execute("""
                    SELECT id, name 
                    FROM tactics 
                    WHERE id = ANY(%s)
                """, (executed_ids,))
                history_rows = cur.fetchall()
                
                for h_row in history_rows:
                    if isinstance(h_row, dict):
                        h_id, h_name = h_row['id'], h_row['name']
                    else:
                        h_id, h_name = h_row[0], h_row[1]
                    
                    executed_names_list.append(f"{h_name} (ID {h_id})")

        if not available_tactics:
            return jsonify({"error": "Nenhuma tática encontrada para esta estratégia"}), 404

        # --- 4. Construção do Prompt ---
        
        # Lista de disponíveis para escolha
        tactics_joined = "\n".join([
            f"- ID {t['id']}: {t['name']} (Tempo: {t['time']} min) | Desc: {t['description']}"
            for t in available_tactics
        ])

        # Lista de histórico formatada com NOMES
        if executed_names_list:
            history_text = ", ".join(executed_names_list)
            history_instruction = f"Táticas já realizadas: [{history_text}]. EVITE repetir o mesmo tipo de tática."
        else:
            history_instruction = "Nenhuma tática executada ainda (Início da sessão)."

        prompt = f"""
        Você é um Arquiteto Pedagógico (Agente de Estratégia).
        Escolha a PRÓXIMA ação de ensino baseada no perfil e histórico.

        === CONTEXTO ===
        Tema: {domain_name}
        Descrição: {domain_description}
        Trecho do Material: {article_text[:500]}...

        === PERFIL DO ALUNO ===
        {student_profile_summary}

        === SITUAÇÃO ATUAL ===
        {performance_summary}
        {history_instruction}

        === OPÇÕES DISPONÍVEIS ===
        {tactics_joined}

        === REGRAS ===
        1. Olhe para o "Táticas já realizadas". Se o aluno já fez um "Vídeo (ID X)", NÃO escolha outro vídeo agora, tente variar (ex: Quiz ou Leitura), a menos que o desempenho peça reforço.
        2. Considere o tempo disponível.
        3. Se o desempenho for RUIM, simplifique. Se for BOM, aprofunde.

        === SAÍDA (JSON) ===
        Responda APENAS:
        {{
            "chosen_tactic_id": 0,
            "tactic_name": "Nome",
            "reasoning": "Por que escolheu esta baseado no histórico e notas."
        }}
        """

        # return jsonify({"prompt": prompt}), 200  # DEBUG: Retorna o prompt para verificação

        # --- 5. Chamada ao Gemini ---
        if not Config.GEMINI_API_KEY:
             return jsonify({"error": "GEMINI_API_KEY não configurada"}), 500

        client = genai.Client(api_key=Config.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite-preview-09-2025", 
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        
        decision_json = json.loads(response.text)

        return jsonify({
            "success": True,
            "decision": decision_json,
            "history_context_used": executed_names_list
        }), 200

    except Exception as e:
        logging.error(f"Erro no Agente Strategies: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()





@agente_strategies_bp.route('/agent/decide_reuse_logic', methods=['POST'])
def decide_reuse_logic():
    """
    Agente de Estratégia (Lógica de Reuso):
    Analisa se a turma absorveu o conteúdo.
    - Se DESEMPENHO BAIXO: Sugere repetir uma tática anterior (Reuso/Reforço).
    - Se DESEMPENHO ALTO: Sugere avançar para uma nova Estratégia do banco.
    """
    data = request.get_json()

    # --- 1. Extração do Contexto (Vindo do Orquestrador) ---
    # Resumo do Control (Notas e Status)
    performance_summary = data.get('performance_summary', 'Sem dados de performance.')
    
    # Resumo do User (Preferências)
    student_profile = data.get('student_profile_summary', 'Perfil desconhecido.')
    
    # Conteúdo do Domain (O que foi ensinado)
    domain_content = data.get('article_text', '')[:1000] # Limita caracteres para não estourar contexto
    
    # Histórico (O que já foi feito)
    current_strategy_id = data.get('strategy_id')
    executed_tactics_ids = data.get('executed_tactics', [])

    conn = None
    try:
        db_url = current_app.config.get("SQLALCHEMY_DATABASE_URI") or os.getenv("DATABASE_URL")
        conn = create_connection(db_url)
        
        if not conn:
            return jsonify({"error": "Falha na conexão com o banco"}), 500

        with conn.cursor() as cur:
            # A. Busca nomes das táticas já executadas (Para sugerir repetição se necessário)
            executed_names = []
            if executed_tactics_ids:
                cur.execute("SELECT id, name FROM tactics WHERE id = ANY(%s)", (executed_tactics_ids,))
                rows = cur.fetchall()
                for r in rows:
                    # Ajuste conforme retorno (Dict ou Tupla)
                    r_id = r['id'] if isinstance(r, dict) else r[0]
                    r_name = r['name'] if isinstance(r, dict) else r[1]
                    executed_names.append(f"{r_name} (ID {r_id})")

            # B. Busca OUTRAS Estratégias disponíveis no banco (Para sugerir mudança)
            # Excluindo a estratégia atual para não sugerir "mudar para o que já estou"
            cur.execute("SELECT id, name FROM strategies WHERE id != %s", (int(current_strategy_id),))
            strat_rows = cur.fetchall()
            available_strategies = []
            for r in strat_rows:
                s_id = r['id'] if isinstance(r, dict) else r[0]
                s_name = r['name'] if isinstance(r, dict) else r[1]
                available_strategies.append(f"Estratégia: {s_name} (ID {s_id})")

        # --- 2. Configuração do Cliente Groq ---
        if not Config.GROQ_API_KEY:
             return jsonify({"error": "GROQ_API_KEY não configurada"}), 500

        client = OpenAI(
            api_key=Config.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )

        # --- 3. Construção do Prompt (Engenharia de Decisão) ---
        prompt = f"""
        Você é um Especialista em Adaptação Pedagógica (Agente de Reuso).
        Sua função é analisar o final de um ciclo de ensino e decidir o próximo passo.

        === DADOS DA TURMA ===
        Perfil: {student_profile}
        Desempenho na Sessão: {performance_summary}
        
        === CONTEXTO DO CONTEÚDO ===
        Trecho do Material: {domain_content}...

        === OPÇÕES DE AÇÃO ===
        1. REPETIR TÁTICA (Reforço):
           Use esta opção se o desempenho for fraco, confuso ou abaixo da média.
           Táticas que podem ser repetidas: {', '.join(executed_names)}
        
        2. MUDAR DE ESTRATÉGIA (Avançar):
           Use esta opção se o desempenho for bom/suficiente e a turma estiver pronta para algo novo.
           Outras estratégias disponíveis: {', '.join(available_strategies)}

        === OBJETIVO ===
        Analise os dados. Se a turma aprendeu, avance. Se não, repita.
        
        === SAÍDA ESPERADA (JSON) ===
        Responda APENAS um JSON neste formato:
        {{
            "decision": "REUSE" ou "CHANGE_STRATEGY",
            "target_id": <ID_DA_TATICA_PARA_REPETIR ou ID_DA_NOVA_ESTRATEGIA>,
            "target_name": "<Nome da Tática ou Estratégia>",
            "reasoning": "<Explicação curta baseada nas notas e perfil>"
        }}
        """

        # --- 4. Chamada ao Modelo (Groq / Llama 3) ---
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Modelo rápido e inteligente da Groq
            messages=[
                {"role": "system", "content": "Responda sempre em JSON válido."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1 # Baixa temperatura para decisão lógica
        )

        content_text = response.choices[0].message.content
        decision_json = json.loads(content_text)

        return jsonify({
            "success": True,
            "analysis": decision_json
        }), 200

    except Exception as e:
        logging.error(f"Erro no Agente Strategies (Reuse): {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()