# pylint: disable=no-value-for-parameter,unused-variable
"""Rotas de Financeiro"""

from flask import Blueprint, jsonify, request, json
from .rest import BotConversaView
from .querys import BotQuerys
from .logistica import busca_motorista, lat_lon_cliente, corrigir_bairro, distancia_destino, enviar_corrida_bot, enviar_mot_cliente

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
@botconversa_app.route('/cancelar_corrida', methods=['POST'])
def cancelar():
    '''Recebe os dados da corrida para repassar
    embarque_cliente
    bairro_embarque
    tel_cliente
    tel_motorista
    bairro_destino'''
    data_json = request.get_json()


    return jsonify({'Cancelado': data_json})


@public_endpoint
@botconversa_app.route('/bloquear', methods=['POST'])
def bloquear():
    ''' Receber informações da corrida e do 
        motorista atual, enviar a corrida
        para outro motorista e voltar o 
        motorista para fila '''


@public_endpoint
@botconversa_app.route('/', methods=['POST'])
def livre():
    data_json = request.get_json()
    telefone = data_json['telefone']
    bairro = corrigir_bairro(data_json['bairro'])
    BotQuerys().livre(telefone, bairro)

    return jsonify({"response": data_json}), 200

@public_endpoint
@botconversa_app.route('/cadastrar', methods=['POST'])
def cadastra_motorista():
    
    data_json = request.get_json()
    telefone = data_json['telefone']
    tipo_carro = data_json['tipo_carro']
    name = data_json['name']
    sexo = data_json['sexo']

    BotQuerys().cadastrar_motorista(name, sexo, telefone, tipo_carro)

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
    cliente_telefone = data_json['cliente_telefone']
    sexo = data_json['sexo'] 
    tel_motorista = data_json.get('mot_telefone')

    # Fila dos Motoristas
    fila_ = [[driver.id, driver.sexo, driver.tipo_carro, driver.lat, driver.lon, driver.name, driver.telefone, driver.bairro, driver.status] for driver in BotQuerys().fila()]

    busca =  lat_lon_cliente(api_key, embarque, bairro_embarque, cidade)
    if busca:
        lat =  busca['latitude']
        lon =  busca['longitude']

    motorista = busca_motorista(api_key, sexo, fila_, lat, lon) 
    cordenadas = BotQuerys().lat_lon_destino(bairro_destino)
    if cordenadas:
        lat_destino = cordenadas['latitude']
        lon_destino = cordenadas['longitude']
        tipo_destino = cordenadas['tipo_destino']

    valores = distancia_destino(api_key, lon_destino, lat_destino, lat, lon)
    print(motorista)
    tipo_bairro =  BotQuerys().tipo_bairro_embarque(bairro_embarque)
    
    if isinstance(motorista, str):
        motorista = json.loads(motorista)  
    else:
        motorista = motorista
    duracao_corrida = valores['duracao'] 
    tempo_para_embarque = motorista['tempo_para_embarque']
    duracao_corrida_int = int(duracao_corrida)
    tempo_para_embarque_int = int(tempo_para_embarque)
    telefone = motorista['telefone']
    tempo_total = duracao_corrida_int + tempo_para_embarque_int 
    tempo_total = str(tempo_total)

    enviar_corrida_bot(motorista, valores, cliente_telefone, tipo_destino, tipo_bairro, bairro_embarque, bairro_destino, embarque)
    enviar_mot_cliente(motorista, valores, cliente_telefone, tipo_destino, tipo_bairro)
    BotQuerys().iniciar_corrida(telefone, tempo_total)
    
   
    if tel_motorista:
        motorista_troca = BotQuerys().buscar_motorista_por_tel(tel_motorista)
        print(motorista_troca)
        if motorista_troca:
            BotQuerys().atualizar_status_motorista(motorista_troca)
            
    return jsonify({"motorista_proximo": motorista }), 200
    
botconversa_view = public_endpoint(BotConversaView.as_view('botconversa_view'))
botconversa_app.add_url_rule('/rest', view_func=botconversa_view)


