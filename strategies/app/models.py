from . import db
from sqlalchemy.types import PickleType

class Strategies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    tatics = db.Column(PickleType, nullable=False, default=[])