from google import genai
from operator import or_
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from app.models import Strategies, Tatics, Message, PrivateMessage
# from app import db  # importar o socketio criado no __init__.py
from db import create_connection
import json


# The client gets the API key from the environment variable `GEMINI_API_KEY`.

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words"
)

print(response.text)



strategies_bp = Blueprint('strategies_bp', __name__)

# @strategies_bp.before_app_request
# def create_tables():
#     db.create_all()