from flask import request, redirect, url_for, render_template, flash, Blueprint, jsonify
from werkzeug.utils import secure_filename
import os
from ..models import Domain, PDF
from .. import db

domain_bp = Blueprint('domain_bp', __name__)

@domain_bp.before_app_request
def create_tables():
    db.create_all()


UPLOAD_FOLDER = 'uploads/'  # ou configure isso no app config

@domain_bp.route('/create', methods=['POST'])
def create_domain():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        files = request.files.getlist('pdfs')

        if not name:
            flash('Name is required')
            return redirect(request.url)

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
        flash('Domain created successfully!')
        return jsonify({"message": "Domain created successfully!"}), 200

    return jsonify({"message": "Domain not created"}), 400


@domain_bp.route('/list', methods=['GET'])
def list_domains():
    domains = Domain.query.all()
    domains_json = [domain.to_dict() for domain in domains]
    return domains_json, 200