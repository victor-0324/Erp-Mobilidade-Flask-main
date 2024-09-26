# pylint: disable=no-value-for-parameter,unused-variable
"""Rotas de Financeiro"""

from flask import Blueprint, jsonify, request
from .rest import BotConversaView
from .querys import BotQuerys
from .logistica import busca_motorista, lat_lon_cliente, corrigir_bairro, atualizar_tarifas, distancia_destino, enviar_corrida_bot

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
    bairro = corrigir_bairro(data_json['bairro'])
    name = data_json['name']
 
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

    api_key = 'pk.f17234d51a1015ab3c5ecb138de627c9' 
    data_json = request.get_json()
    bairro_embarque = corrigir_bairro(data_json['bairro_embarque'])
    embarque = data_json['embarque']
    cidade = 'São Lourenço MG 37470000'
    bairro_destino = corrigir_bairro(data_json['bairro_destino'])
   
    # Fila dos Motoristas
    fila_ = [[driver.id, driver.lat, driver.lon, driver.name, driver.telefone, driver.bairro] for driver in BotQuerys().fila()]

    busca =  lat_lon_cliente(api_key, embarque, bairro_embarque, cidade)
    if busca:
        lat =  busca['latitude']
        lon =  busca['longitude']
    motorista = busca_motorista(api_key, fila_, lat, lon) 

    cordenadas = BotQuerys().lat_lon_destino(bairro_destino)
    if cordenadas:
        lat_destino = cordenadas['latitude']
        lon_destino = cordenadas['longitude']
        tipo_destino = cordenadas['tipo_destino']

    valores = distancia_destino(api_key, lon_destino, lat_destino, lat, lon)
    print(valores)
    
    tipo_bairro =  BotQuerys().tipo_bairro_embarque(bairro_embarque)
    enviar_corrida_bot(motorista, valores, tipo_destino, tipo_bairro, bairro_embarque, embarque)
   
    return jsonify({"motorista_proximo": motorista }), 200
    

@public_endpoint
@botconversa_app.route('/tarifas', methods=['POST'])
def tarifa():
    ''' Calcula e modifica os valores das tarifas '''
    
    data_json = request.get_json()
    print(f'Dados recebido: {data_json}')
    dados = atualizar_tarifas(data_json)

    print(f'Valor alterado: {dados}')
    
    return jsonify({"motorista_proximo": dados }), 200



@public_endpoint
@botconversa_app.route('/fila/sair', methods=['POST'])
def sair():
    data_json = request.get_json()
    telefone = data_json['telefone']
    BotQuerys().sair_da_fila(telefone)
    return jsonify({"response": "removido"}), 200


botconversa_view = public_endpoint(BotConversaView.as_view('botconversa_view'))
botconversa_app.add_url_rule('/rest', view_func=botconversa_view)


