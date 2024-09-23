# pylint: disable=no-value-for-parameter,unused-variable
"""Rotas de Financeiro"""
import requests

from flask import Blueprint, jsonify, request

from .rest import BotConversaView
from .querys import BotQuerys

from .logistica import logistica, busca_lat_lon

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

     # faz requisição para o botconversa api
    url = f'https://backend.botconversa.com.br/api/v1/webhook/subscriber/get_by_phone/{telefone}/'
    token = data_json['token']

    # consulta o nome pelo telefone
    data_driver = requests.get(
        url,
        headers={"API-KEY": token},
        timeout=30
    ).json()
    
    name = data_driver.get('full_name')
 

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

    bairro_embarque = data_json['bairro_embarque']
    embarque = data_json['embarque']
    cidade = 'São Lourenço MG 37470000'
    bairro_destino =  data_json['bairro_destino']
    fila_ = [[driver.id, driver.lat, driver.lon, driver.name, driver.telefone, driver.bairro] for driver in BotQuerys().fila()]

    api_url = 'https://backend.botconversa.com.br/api/v1/webhooks-automation/catch/87780/FTD5inieIqwk/'
    key = '26084536-20e3-4c12-98fc-dd6b30ba2417' 

    # Parâmetros da requisição
    params = {
        'bairro_embarque': bairro_embarque,
        'embarque': embarque
    }

    # Headers com a chave de autenticação
    headers = {
        'Authorization': f'Bearer {key}',  # Se a API precisar da chave como Bearer
        'Content-Type': 'application/json'  # Definindo o tipo de conteúdo
    }


    # Fazendo a requisição POST
    response = requests.post(api_url, json=params, headers=headers, timeout=30)

    # Verificando e imprimindo o resultado
    if response.status_code == 200:
        print("Requisição bem-sucedida!")
        print(response.json())  # Exibe a resposta em JSON
    else:
        print(f"Erro na requisição: {response.status_code}")
        print(response.text)



    busca =  busca_lat_lon(api_key, embarque, bairro_embarque, cidade)
    lat =  busca['latitude']
    lon =  busca['longitude']
    
    resultado = logistica(api_key, fila_, lat, lon)
    print(resultado)

    return jsonify({"motorista_proximo": resultado }), 200
    

@public_endpoint
@botconversa_app.route('/fila/sair', methods=['POST'])
def sair():
    data_json = request.get_json()
    telefone = data_json['telefone']
    BotQuerys().sair_da_fila(telefone)
    return jsonify({"response": "removido"}), 200


botconversa_view = public_endpoint(BotConversaView.as_view('botconversa_view'))
botconversa_app.add_url_rule('/rest', view_func=botconversa_view)


  # motorista_proximo = BotQuerys().calcular_motorista_mais_proximo(lat, lon)
    
    # # Verifique se encontrou algum motorista
    # if motorista_proximo:
    #     motorista_dict = {
    #         'id': motorista_proximo.DriverQueue.id,
    #         'name': motorista_proximo.DriverQueue.name,
    #         'telefone': motorista_proximo.DriverQueue.telefone,
    #         'lat': motorista_proximo.DriverQueue.lat,
    #         'lon': motorista_proximo.DriverQueue.lon,
    #         'bairro': motorista_proximo.DriverQueue.bairro,
    #         'distancia': motorista_proximo.distancia  # Distância calculada
    #     }
    #     print(f'O Motorista mais próximo é {motorista_dict["name"]} no bairro {motorista_dict["bairro"]}')
        
    #     resultado = obter_distancia(api_key, lat, lon)
    #     print(resultado)