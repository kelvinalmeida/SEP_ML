from flask import Blueprint, render_template, request, redirect, url_for, make_response, flash, jsonify
from requests.exceptions import RequestException
from .auth import token_required
import requests

from .auth import verificar_cookie
from .services_routs import DOMAIN_URL

domain_bp = Blueprint("domain", __name__)

@domain_bp.route("/domain/create", methods=["GET", "POST"])
@token_required
def create_domain(current_user=None):
    if request.method == "POST":
        # Captura dados do formulário do usuário
        name = request.form.get("name")
        description = request.form.get("description")
        files = request.files.getlist("pdfs")

        # Monta os dados do formulário para enviar ao microserviço
        data = {
            'name': name,
            'description': description
        }


        # Monta os arquivos
        files_payload = [
            ('pdfs', (file.filename, file.stream, file.content_type))
            for file in files
        ]

        # Envia via POST para o microserviço
        response = requests.post(f"{DOMAIN_URL}/create", data=data, files=files_payload)

        if response.ok:
            flash("Domain created successfully!")
        else:
            flash("Failed to create domain.")

        return redirect(url_for('domain.create_domain'))

    return render_template('/domain/create_domain.html')  # Página com formulário


