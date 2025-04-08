from flask import Blueprint, jsonify, render_template
import requests


gateway_bp = Blueprint('gateway_bp', __name__)

USER_URL = 'http://localhost:5001'
CONTROL_URL = 'http://localhost:5002'

@gateway_bp.route("/")
def login_page():
    return render_template("index.html")

@gateway_bp.route('/students', methods=['GET'])
def get_students():
    response = requests.get(f"{USER_URL}/students")
    return (response.text, response.status_code, response.headers.items())

@gateway_bp.route('/teachers', methods=['GET'])
def get_taachers():
    response = requests.get(f"{USER_URL}/teachers")
    return (response.text, response.status_code, response.headers.items())

@gateway_bp.route('/sessions', methods=['GET'])
def list_sessions():
    response = requests.get(f"{CONTROL_URL}/sessions")
    return (response.text, response.status_code, response.headers.items())