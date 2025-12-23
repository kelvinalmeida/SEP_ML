from flask import Blueprint, jsonify, request
import os
from google import genai
import json

agente_control_bp = Blueprint('agente_control_bp', __name__)

@agente_control_bp.route('/agent/decide_next_tactic', methods=['POST'])
def decide_next_tactic():
    data = request.get_json()

    article_text = data.get('article_text')
    student_summary = data.get('student_preference_summary')
    available_tactics = data.get('available_tactics') # List of dicts: {'id': 1, 'name': '...', 'description': '...'}

    if not article_text or not available_tactics:
        return jsonify({"error": "Missing required data"}), 400

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
         return jsonify({"error": "GEMINI_API_KEY not set"}), 500

    client = genai.Client(api_key=api_key)

    tactics_str = json.dumps(available_tactics, indent=2)

    prompt = f"""
    You are an Expert Pedagogical Agent.

    Context:
    - Domain Content (Article): {article_text[:2000]}... (truncated)
    - Student Learning Profile: {student_summary}
    - Available Tactics: {tactics_str}

    Task:
    Analyze the domain content and the student's profile to choose the most suitable next tactic from the available list.

    Output Format (JSON only):
    {{
        "chosen_tactic_id": <id>,
        "justification": "<short reasoning>"
    }}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        result = json.loads(response.text)
    except Exception as e:
        # Fallback if JSON parsing fails or API error
        return jsonify({"error": str(e), "raw_response": getattr(response, 'text', '')}), 500

    return jsonify(result)
