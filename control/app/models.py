from . import db
from sqlalchemy.types import PickleType
from datetime import datetime

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=False)
    strategies = db.Column(PickleType, nullable=False, default=[])
    teachers = db.Column(PickleType, nullable=False, default=[])
    students = db.Column(PickleType, nullable=False, default=[])
    domains = db.Column(PickleType, nullable=False, default=[])
    start_time = db.Column(db.DateTime)  # Novo campo para armazenar o horário de início