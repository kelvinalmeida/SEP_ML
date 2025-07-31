from . import db
from sqlalchemy.types import PickleType
from datetime import datetime

from sqlalchemy.exc import IntegrityError
import random
import string

from sqlalchemy.ext.mutable import MutableList


def generate_unique_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=False)
    strategies = db.Column(MutableList.as_mutable(PickleType), nullable=False, default=list)
    teachers = db.Column(MutableList.as_mutable(PickleType), nullable=False, default=list)
    students = db.Column(MutableList.as_mutable(PickleType), nullable=False, default=list)
    domains = db.Column(MutableList.as_mutable(PickleType), nullable=False, default=list)

    code = db.Column(db.String(50), nullable=False, unique=True)
    start_time = db.Column(db.DateTime)

    verified_answers = db.relationship('VerifiedAnswers', backref='session', lazy='joined')
    estra_notes = db.relationship('ExtraNotes', backref='session', lazy='joined')

    def __init__(self, *args, **kwargs):
        if 'code' not in kwargs:
            # Garante unicidade tentando até gerar um código único
            while True:
                generated_code = generate_unique_code()
                if not Session.query.filter_by(code=generated_code).first():
                    kwargs['code'] = generated_code
                    break
        super().__init__(*args, **kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'strategies': self.strategies,
            'teachers': self.teachers,
            'students': self.students,
            'code': self.code,
            'domains': self.domains,
            'start_time': self.start_time,
            'verified_answers': [va.to_dict() for va in self.verified_answers],
            'extra_notes': [en.to_dict() for en in self.estra_notes]
        }

    
class ExtraNotes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    estudante_username = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.Integer, nullable=False)
    extra_notes = db.Column(db.Float, nullable=False, default=0.0)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'estudante_username': self.estudante_username,
            'extra_notes': self.extra_notes,
            'session_id': self.session_id
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