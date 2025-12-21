from flask import Blueprint, request, jsonify

agente_strategies_bp = Blueprint('agente_strategies', __name__)

@agente_strategies_bp.route('/strategies/validate', methods=['POST'])
def validate_strategy():
    data = request.get_json()
    strategy = data.get('strategy', {})
    domain_info = data.get('domain_info', {})

    score = 100
    feedback = []

    name = strategy.get('name')
    if not name or len(name) < 3:
        score -= 10
        feedback.append("O nome da estratégia é muito curto.")

    tactics = strategy.get('tactics', [])
    if not tactics:
        score -= 50
        feedback.append("Adicione pelo menos uma tática.")
    else:
        total_time = sum(float(t.get('time', 0)) for t in tactics)
        if total_time == 0:
            score -= 20
            feedback.append("O tempo total não pode ser zero.")

    if score < 0: score = 0

    if not feedback:
        feedback.append("A estratégia parece boa!")

    return jsonify({"score": score, "feedback": feedback}), 200
