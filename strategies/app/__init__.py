import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
# socketio = SocketIO()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///../instance/users.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['SECRET_KEY'] = 'sua_chave_super_secreta'

    from app.routes.strategies_routes import strategies_bp
    # Registrar o blueprint
    app.register_blueprint(strategies_bp)


    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    # socketio.init_app(app)

    return app
