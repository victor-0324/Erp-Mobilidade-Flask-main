# pylint: disable=no-value-for-parameter,unused-variable
"""Rotas de Financeiro"""
import requests

from flask import Blueprint, jsonify, request

from .rest import BotConversaView
from .querys import BotQuerys

# from .logistica import logistica
from .src import (
    dados_usuario_por_telefone,
    enviar_corrida  
)


botconversa_app = Blueprint(
    "botconversa_app", __name__, url_prefix="/botconversa/")


def public_endpoint(function):
    """Decorator for public routes"""
    function.is_public = True
    return function


@public_endpoint
@botconversa_app.route('/', methods=['POST'])
def add_driver():
    data_json = request.get_json()
    telefone = data_json['telefone']
    bairro = data_json['bairro']
    url = f'https://backend.botconversa.com.br/api/v1/webhook/subscriber/get_by_phone/{telefone}/'
    token = data_json['token']

    # faz requisição para o botconversa api
    # consulta o nome pelo telefone
    data_driver = requests.get(
        url,
        headers={"API-KEY": token},
        timeout=30
    ).json()
    
    name = data_driver.get('full_name')

    if not bairro:
        bairro = 'Centro'

    # print(name, bairro)

    BotQuerys().novo(name, telefone, bairro)

    return jsonify({"response": data_json}), 200


@public_endpoint
@botconversa_app.route('/fila', methods=['get'])
def fila():
    """Retorna a fila de motoristas"""
    fila_ = [[driver.name, driver.bairro, driver.date_time, driver.telefone]
             for driver in BotQuerys().fila()]
    return jsonify({"response": fila_}), 200


@public_endpoint
@botconversa_app.route('/corrida', methods=['POST'])
def corrida():
    """Envia uma corrida
    Embarque
    bairro_embarque
    bairro_destino
    telefone"""

    data_json = request.get_json()

    # 
    cliente = data_json['bairro_origem']
    
    cliente_id = dados_usuario_por_telefone(data_json['telefone']).get('id')

    # Varifica o motorista mais proximo e remove ele da fila
    fila_ = [[driver.bairro, driver.telefone] for driver in BotQuerys().fila()]
    print(fila_)

    motorista_telefone = logistica(fila_, cliente)
    BotQuerys().remove_first_driver(motorista_telefone)
    motorista = dados_usuario_por_telefone(motorista_telefone)

    # Enviar fluxo da corrida para o cliente, e já envia para o motorista
    enviar_corrida(cliente_id, motorista)

    return jsonify({"response": motorista}), 200


@public_endpoint
@botconversa_app.route('/fila/sair', methods=['POST'])
def sair():
    data_json = request.get_json()
    telefone = data_json['telefone']
    BotQuerys().sair_da_fila(telefone)
    return jsonify({"response": "removido"}), 200


botconversa_view = public_endpoint(BotConversaView.as_view('botconversa_view'))
botconversa_app.add_url_rule('/rest', view_func=botconversa_view)
