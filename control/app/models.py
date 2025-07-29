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
    verified_answers = db.relationship('VerifiedAnswers', backref='session', lazy='joined');

    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'strategies': self.strategies,
            'teachers': self.teachers,
            'students': self.students,
            'domains': self.domains,
            'start_time': self.start_time,
            'verified_answers': [va.to_dict() for va in self.verified_answers]
        }


class VerifiedAnswers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(50), nullable=False)
    answers = db.Column(PickleType, nullable=False)  # Array de respostas do aluno
    score = db.Column(db.Integer, nullable=False, default=0)  # Novo campo para armazenar a pontuação
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'student_name': self.student_name,
            'student_id': self.student_id,
            'answers': self.answers,
            'score': self.score,  # Incluindo a pontuação no dicionário
            'session_id': self.session_id
        }