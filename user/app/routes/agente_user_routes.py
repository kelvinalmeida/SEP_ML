import logging
from flask import Blueprint, request, jsonify
# ATENÇÃO: Importação do novo SDK
from google import genai
from ..models import Student
from config import Config

agente_user_bp = Blueprint('agente_user_bp', __name__)

@agente_user_bp.route('/students/summarize_preferences', methods=['POST'])
def summarize_preferences():
    """
    Agente User: Recebe IDs, busca no Postgres e resume com Gemini (Novo SDK).
    """
    data = request.get_json()
    student_ids = data.get('student_ids', [])

    if not student_ids:
        return jsonify({"summary": "Nenhum estudante selecionado."}), 200

    try:
        # 1. Busca no Postgres (SQLAlchemy)
        students = Student.query.filter(Student.id.in_(student_ids)).all()

        if not students:
            return jsonify({"summary": "Estudantes não encontrados."}), 404

        # 2. Prepara o texto
        profiles_text = []
        for s in students:
            # Garanta que o nome do campo 'learning_style' está correto no seu Model
            pref = getattr(s, 'learning_style', 'Preferência não informada') 
            profiles_text.append(f"- Aluno {s.name}: {pref}")
        
        profiles_joined = "\n".join(profiles_text)

        # 3. Chamada ao Gemini usando o NOVO SDK (Client)
        prompt = f"""
        Atue como um Especialista Pedagógico.
        Analise estas preferências de aprendizado:
        {profiles_joined}
        
        Gere um resumo curto (1 parágrafo) sobre o perfil da turma para guiar a aula.
        """

        # Instancia o cliente com a chave do Config
        client = genai.Client(api_key=Config.GEMINI_API_KEY)
        
        # Gera o conteúdo
        # Nota: O modelo 'gemini-2.5-flash' do seu exemplo pode não estar disponível
        # publicamente para todos ainda. Use 'gemini-1.5-flash' para garantir estabilidade.
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )

        return jsonify({
            "summary": response.text,
            "student_count": len(students)
        }), 200

    except Exception as e:
        logging.error(f"Erro no Agente User: {str(e)}")
        # Tratamento para erros específicos da API (opcional)
        return jsonify({"error": str(e)}), 500