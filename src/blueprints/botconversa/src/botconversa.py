"""Funções de botconversa."""

import requests
from flask import jsonify

api_key_ = {"API-KEY": "f73c9b09-2a4c-46a7-acce-3e4fc8fde137"}


def dados_usuario_por_telefone(telefone):
    """Retorna dados do usuario pelo telefone."""
    url = f'https://backend.botconversa.com.br/api/v1/webhook/subscriber/get_by_phone/{telefone}/'

    data_driver = requests.get(
        url,
        headers=api_key_,
        timeout=30
    ).json()
    
    return data_driver


def atualizar_campo(usuario, campo_id, valor):
    """Atualiza campo do usuario."""
    url = f'https://backend.botconversa.com.br/api/v1/webhook/subscriber/{usuario}/custom_fields/{campo_id}/'

    requests.post(
        url,
        headers=api_key_,
        data=jsonify({"value": valor}),
        timeout=30
    )


def consultar_fluxo_pelo_nome(nome):
    """Consulta fluxo pelo nome."""
    url = 'https://backend.botconversa.com.br/api/v1/webhook/flows/'

    fluxos = requests.get(
        url,
        headers=api_key_,
        timeout=30
    ).json()

    return next((item for item in fluxos if item["name"] == nome), None)

# rota para retornar que o servidor esta funcionando

def enviar_fluxo(usuario_id, fluxo_id):
    """Envia fluxo para o usuario."""
    url = f'https://backend.botconversa.com.br/api/v1/webhook/subscriber/{usuario_id}/send_flow/'

    requests.post(
        url,
        headers=api_key_,
        data=jsonify({"flow": fluxo_id}),
        timeout=30
    )


def enviar_corrida(cliente_id, motorista):
    """Envia corrida"""

    # Enviar fluxo da corrida para o cliente_id
    fluxo = consultar_fluxo_pelo_nome(motorista)
    enviar_fluxo(cliente_id, fluxo)
