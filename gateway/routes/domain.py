from flask import Blueprint, render_template, request, redirect, url_for, make_response, flash, jsonify, Response
from requests.exceptions import RequestException
from .auth import token_required
import requests

from .auth import verificar_cookie
from .services_routs import DOMAIN_URL

domain_bp = Blueprint("domain", __name__)

@domain_bp.route("/domains/create", methods=["GET", "POST"])
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
        response = requests.post(f"{DOMAIN_URL}/domains/create", data=data, files=files_payload)

        if response.ok:
            return render_template('/domain/success.html')
        else:
            flash(f"Falha ao criar domínio. {response.status_code} - {response.text}")


        return redirect(url_for('domain.create_domain'))

    return render_template('/domain/create_domain.html')  # Página com formulário


@domain_bp.route("/domains", methods=["GET"])
@token_required
def list_domains(current_user=None):
    try:
        # Faz uma requisição GET para o microserviço de domínio
        response = requests.get(f"{DOMAIN_URL}/domains")
        response.raise_for_status()  # Levanta um erro se a resposta não for 200 OK
        domains = response.json()
    except RequestException as e:
        flash("Failed to fetch domains.")
        domains = []

    return render_template("/domain/list_domains.html", domains=domains)
    # return jsonify(domains), 200  # Retorna a lista de domínios em formato JSON


@domain_bp.route("/domains/<int:domain_id>", methods=["GET"])
@token_required
def get_domain(current_user=None, domain_id=None):
    try:
        # Faz uma requisição GET para o microserviço de domínio
        response = requests.get(f"{DOMAIN_URL}/domains/{domain_id}")
        response.raise_for_status()  # Levanta um erro se a resposta não for 200 OK
        domain = response.json()
    except RequestException as e:
        flash("Failed to fetch domain.")
        domain = None

    
    # return f"{domain}"

    return render_template("/domain/domain_detail.html", domain=domain)
    # return jsonify(domain), 200  # Retorna os detalhes do domínio em formato JSON


@domain_bp.route('/pdfs/<int:pdf_id>', methods=['GET'])
@token_required
def proxy_pdf_download(current_user=None, pdf_id=None):
    try:
        # Requisição para o domínio
        response = requests.get(f"{DOMAIN_URL}/pdfs/{pdf_id}", stream=True)
        response.raise_for_status()

        # Pega o nome original do arquivo do header
        content_disposition = response.headers.get('Content-Disposition')
        filename = "download.pdf"
        if content_disposition and 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[1].strip('"')

        # Retorna o conteúdo como download para o usuário
        return Response(
            response.iter_content(chunk_size=8192),
            content_type=response.headers['Content-Type'],
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except RequestException:
        return "Failed to download file", 500
