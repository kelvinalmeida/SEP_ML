from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Caminho para o banco dentro da pasta 'instance'
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///../instance/sessions.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from app.routes.strategies_routes import strategies_bp
    # Registrar o blueprint
    app.register_blueprint(strategies_bp)

    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)

    return app
