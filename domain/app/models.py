from . import db

class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    
    pdfs = db.relationship('PDF', backref='domain', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'pdfs': [pdf.to_dict() for pdf in self.pdfs]
        }

class PDF(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)  # nome do arquivo
    path = db.Column(db.String(255), nullable=False)       # caminho do arquivo salvo
    domain_id = db.Column(db.Integer, db.ForeignKey('domain.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'path': self.path,
            'domain_id': self.domain_id
        }
