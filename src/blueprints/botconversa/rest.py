# pylint: disable=no-value-for-parameter,unused-variable
"""Rotas de Dashboard"""


import requests
from flask.views import MethodView
from flask import request, jsonify


class BotConversaView(MethodView):
    """CRUD de Financeiro"""

    def post(self):
        """Retorna o json da requisição"""
        data_json = request.get_json()
        url = data_json.pop("url")        
        response = requests.post(
            url,
            headers = {"Content-Type": "application/json"},
            json=data_json,
            timeout=30,
            ),

        return jsonify({"response": data_json}), 200
