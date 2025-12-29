import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify, Blueprint
import sys
import os
import json
import jwt
from datetime import datetime, timedelta

# Adjust path to import from gateway
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from gateway.routes.orchestrator.agente_user.agente_user_routes import agete_user_bp

class TestAgenteUserAggregation(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'super_secret_test_key'
        self.app.register_blueprint(agete_user_bp)

        login_bp = Blueprint('login', __name__)
        @login_bp.route('/login')
        def login():
            return "Login Page"
        self.app.register_blueprint(login_bp)

        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

    def get_auth_token(self):
        token = jwt.encode({
            'username': 'student_test',
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, self.app.secret_key, algorithm="HS256")
        return token

    @patch('gateway.routes.orchestrator.agente_user.agente_user_routes.requests.get')
    def test_ask_tutor_aggregation(self, mock_get):
        token = self.get_auth_token()
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        # Try setting cookie without server_name, just in case
        try:
            self.client.set_cookie('access_token', token)
        except TypeError:
            # Fallback to standard signature
            self.client.set_cookie('localhost', 'access_token', token)

        # 2. Mock Service Responses
        def get_side_effect(url, *args, **kwargs):
            if 'grades_history' in url:
                return MagicMock(status_code=200, json=lambda: {
                    '100': {'notes': [8.0], 'extra_notes': [1.0]}
                })
            if 'chat_history' in url:
                return MagicMock(status_code=200, json=lambda: {
                    '501': {'general': ['msg1'], 'private': []},
                    '999': {'general': ['spam'], 'private': []}
                })
            if '/sessions/100' in url:
                return MagicMock(status_code=200, json=lambda: {
                    'id': 100,
                    'domain_id': '200',
                    'original_strategy_id': '300',
                    'strategies': ['300'],
                    'domains': ['200']
                })
            if '/domains/200' in url:
                return MagicMock(status_code=200, json=lambda: {
                    'name': 'Matematica Avancada',
                    'description': 'Calculo e Algebra',
                    'pdfs': [{'filename': 'calc.pdf', 'path': '/p/calc.pdf'}],
                    'videos_youtube': [{'url': 'http://yt.com/abc', 'title': 'YT Vid'}],
                    'videos_uploaded': []
                })
            if '/strategies/300' in url:
                return MagicMock(status_code=200, json=lambda: {
                    'id': 300,
                    'tatics': [
                        {'id': 501, 'name': 'Debate', 'description': '...'},
                        {'id': 502, 'name': 'Quiz', 'description': '...'}
                    ]
                })
            return MagicMock(status_code=404)

        mock_get.side_effect = get_side_effect

        # 3. Execute Request
        response = self.client.post('/orchestrator/student/ask_tutor',
                                    json={'prompt': 'Help me with limits'})

        if response.status_code != 200:
             print(f"FAILED Response Status: {response.status_code}")
             print(f"FAILED Response Body: {response.data}")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['student_username'], 'student_test')
        self.assertIn('Matematica Avancada', data['study_context'])
        domain_ctx = data['study_context']['Matematica Avancada']
        self.assertEqual(len(domain_ctx['sessions_history']), 1)
        session = domain_ctx['sessions_history'][0]
        interaction = session['interactions'][0]
        self.assertEqual(str(interaction['tactic_id']), '501')

if __name__ == '__main__':
    unittest.main()
