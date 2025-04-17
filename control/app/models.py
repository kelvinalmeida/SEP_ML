from . import db
from sqlalchemy.types import PickleType

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=False)
    strategies = db.Column(PickleType, nullable=False, default=[])
    teachers = db.Column(PickleType, nullable=False, default=[])
    students = db.Column(PickleType, nullable=False, default=[])
    
