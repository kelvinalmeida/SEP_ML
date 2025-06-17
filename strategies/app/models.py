from . import db 
from sqlalchemy.types import PickleType
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime
from sqlalchemy.orm import relationship


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
    __tablename__ = 'message' # Nome da tabela explícito é uma boa prática
    id = db.Column(db.Integer, primary_key=True)
    
    # 1. Campo para mensagens gerais, mantido como você pediu.
    messages = db.Column(MutableList.as_mutable(PickleType), nullable=False, default=list)
    
    # 2. Relação com PrivateMessage. Substitui o antigo campo 'menssages_privates'.
    #    Agora, isso vai conter uma lista de objetos PrivateMessage.
    messages_privates = relationship("PrivateMessage", back_populates="message_parent", cascade="all, delete-orphan")

    def as_dict(self):
        return {
            "id": self.id,
            "messages": self.messages,
            # Mapeia cada objeto PrivateMessage para o seu formato de dicionário
            "messages_privates": [pm.as_dict() for pm in self.messages_privates]
        }


class PrivateMessage(db.Model):
    __tablename__ = 'private_message'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, nullable=False)
    receiver_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(80), nullable=False) # CAMPO ADICIONADO
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    message_parent = relationship("Message", back_populates="messages_privates")

    def as_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "username": self.username, # CAMPO ADICIONADO
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }