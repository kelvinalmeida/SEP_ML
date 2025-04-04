# 📌 Fluxo Resumido
# 1️⃣ Usuário faz login (/auth/login) → Verifica credenciais com o microserviço de usuário.
# 2️⃣ ✅ Professor cria sessão (/session/create) → Registra sessão e aguarda alunos.
# 2️⃣ ✅ Lista todas as sesões (/sessions) → Exibe sessões ativas e inativas.
# 3️⃣ ✅ Alunos acessam sessão (/sessions/status/{session_id}) → Verificam status da aula.
# 3️⃣ ✅ Obtem a sessao (/sessions/{session_id}) 
# 4️⃣ ✅ Se necessário, inicia o debate (/sessions/start/{session_id}).
# 6️⃣ ✅ Sessão finalizada pelo professor (/sessions/end/{session_id}).

# 📌 Conclusão
# 🔹 O Controle funciona como um coordenador entre os microserviços.
# 🔹 Ele não executa as ações diretamente, mas chama outros microserviços.
# 🔹 Facilita a expansão e manutenção da arquitetura baseada em microserviços.

# ⚡ Agora, você pode começar a implementar os endpoints no Flask! Quer um exemplo prático? 🚀



from flask import Flask, request, jsonify, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import redirect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sessions.db'  # Banco SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo da tabela Session
class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=False)
    strategy = db.Column(db.String(50), nullable=False)

# Criar tabelas antes da primeira requisição
@app.before_request
def create_tables():
    db.create_all()

# Página principal de criação da sessão
@app.route('/session/create', methods=['GET', 'POST'])
def create_session():
    if request.method == 'POST':
        # Obtendo dados do formulário
        status = "aguardando"
        strategy = request.form['strategy']

        # Criando a nova sessão
        new_session = Session(status=status, strategy=strategy)

        # Adicionando a sessão ao banco de dados
        db.session.add(new_session)
        db.session.commit()

        # Redirecionando para a página de sucesso
        return redirect(url_for('success'))

    return render_template('create_session.html')  # Exibe o formulário


# Página de sucesso após a criação da sessão
@app.route('/success')
def success():
    return 'Sessão criada com sucesso!'


@app.route('/sessions', methods=['GET'])
def list_sessions():
    # Busca todas as sessões no banco de dados
    all_sessions = Session.query.all()
    return render_template('list_sessions.html', sessions=all_sessions)


@app.route('/session/status/<int:session_id>', methods=['GET'])
def get_session_status(session_id):
    """Obtém o status de uma sessão ativa."""
    session = Session.query.get(session_id)
    if session:
        return jsonify({"session_id": session.id, "status": session.status})
    return jsonify({"error": "Session not found"}), 404


@app.route('/session/start/<int:session_id>', methods=['POST'])
def end(session_id):
    """Finaliza uma inicia de ensino."""
    session = Session.query.get(session_id)
    session.status = "in-progress"
    db.session.commit()
    if session:
        return jsonify({"session_id": session.id, "status": session.status}), 200
    return jsonify({"error": "Session not found"}), 404


@app.route('/session/end/<int:session_id>', methods=['POST'])
def end_session(session_id):
    """Finaliza uma sessão de ensino."""
    session = Session.query.get(session_id)
    if session:
        session.status = "finished"
        db.session.commit()
        return jsonify({"session_id": session.id, "message": "Session ended!"})
    return jsonify({"error": "Session not found"}), 404


print(app.url_map)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
