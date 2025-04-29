from . import db 
from sqlalchemy.types import PickleType
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime

class Strategies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    tatics = db.Column(PickleType, nullable=False, default=list)  # Melhor prática que usar []

class Tatics:
    def __init__(self, name, description, time, chat_id = None):
        self.name = name
        self.description = description
        self.time = time
        self.chat_id = chat_id

    def __repr__(self):
        return f"<Tatics name={self.name}, description={self.description}, time={self.time}, chat_id={self.chat_id}>"

    def as_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "time": self.time,
            "chat_id": self.chat_id if self.chat_id else None 
        }

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    messages = db.Column(MutableList.as_mutable(PickleType), nullable=False, default=list)

    def as_dict(self):
        return {
            "id": self.id,
            "messages": self.messages
        }


