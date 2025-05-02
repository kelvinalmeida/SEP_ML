from flask import request, redirect, url_for, render_template, send_file, Blueprint, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from ..models import Domain, PDF
from .. import db
import os


domain_bp = Blueprint('domain_bp', __name__)

@domain_bp.before_app_request
def create_tables():
    db.create_all()


# ou configure isso no app config

@domain_bp.route('/domains/create', methods=['POST'])
def create_domain():
    UPLOAD_FOLDER = os.path.join(current_app.root_path, 'uploads')

    # return f"{UPLOAD_FOLDER}", 200
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        files = request.files.getlist('pdfs')

        new_domain = Domain(name=name, description=description)
        db.session.add(new_domain)
        db.session.commit()

        for file in files:
            if file and file.filename.endswith('.pdf'):
                filename = secure_filename(file.filename)
                path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(path)

                pdf = PDF(filename=filename, path=path, domain_id=new_domain.id)
                db.session.add(pdf)

        db.session.commit()
        return jsonify({"message": "Domain created successfully!"}), 200

    return jsonify({"message": "Domain not created"}), 400


@domain_bp.route('/domains', methods=['GET'])
def list_domains():
    domains = Domain.query.all()
    domains_json = [domain.to_dict() for domain in domains]
    return domains_json, 200


@domain_bp.route('/domains/<int:domain_id>', methods=['GET'])
def get_domain(domain_id):
    domain = Domain.query.get_or_404(domain_id)
    return jsonify(domain.to_dict()), 200


@domain_bp.route('/pdfs/<int:pdf_id>', methods=['GET'])
def download_pdf(pdf_id):
    pdf = PDF.query.get_or_404(pdf_id)
    file_path = pdf.path
    

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    return send_file(file_path, as_attachment=True)
