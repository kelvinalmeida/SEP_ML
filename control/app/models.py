from . import db

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=False)
    strategy = db.Column(db.String(50), nullable=False)
