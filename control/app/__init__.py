import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Caminho para o banco dentro da pasta 'instance'
    # app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///../instance/sessions.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///../instance/users.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)

    # Registrar blueprints
    from app.routes.session_routes import session_bp
    app.register_blueprint(session_bp)

    return app
