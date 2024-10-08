# pylint: disable=no-value-for-parameter,unused-variable
"""Rotas de Financeiro"""

from flask import Blueprint, jsonify, request, json
from .rest import BotConversaView
from .querys import BotQuerys
from .logistica import busca_motorista, enviar_corrida_bot_None, lat_lon_cliente, corrigir_bairro, distancia_destino, enviar_corrida_bot, enviar_mot_cliente


botconversa_app = Blueprint(
    "botconversa_app", __name__, url_prefix="/botconversa/")


def public_endpoint(function):
    """Decorator for public routes"""
    function.is_public = True
    return function

@public_endpoint
@botconversa_app.route('/', methods=['POST'])
def livre():
    data_json = request.get_json()
    telefone = data_json['telefone']
    bairro = corrigir_bairro(data_json['bairro'])
    BotQuerys().livre(telefone, bairro)

    return jsonify({"response": data_json}), 200

@public_endpoint
@botconversa_app.route('/corrida', methods=['POST'])
def corrida():
    """Envia uma corrida
    Embarque
    bairro_embarque
    bairro_destino
    telefone"""
    # Dados recebido no post
    api_key = 'pk.f17234d51a1015ab3c5ecb138de627c9' 
    data_json = request.get_json()
    bairro_embarque = corrigir_bairro(data_json['bairro_embarque'])
    embarque = data_json['embarque']
    cidade = 'São Lourenço MG 37470000'
    bairro_destino = corrigir_bairro(data_json['bairro_destino'])
    cliente_telefone = data_json['cliente_telefone']
    sexo = data_json['prefere_sexo'] 
    tel_motorista = data_json.get('mot_telefone') 
    tipo_carro = data_json['prefere_carro']

    print(data_json)  
    # Fila dos Motoristas cadastrado no banco
    fila_ = [[driver.id, driver.sexo, driver.tipo_carro, driver.lat, driver.lon, driver.name, driver.telefone, driver.bairro, driver.status, driver.cliente_bloqueado, driver.hora_livre] for driver in BotQuerys().fila()]
   
    # Busca latitude e longetude do cliente
    busca =  lat_lon_cliente(api_key, embarque, bairro_embarque, cidade)
    if busca:
        lat =  busca['latitude']
        lon =  busca['longitude']

    print(f" Lat e lon cliente {busca}")
    # Busca os motorista com base nas preferencias do cliente
    motorista = busca_motorista(api_key, bairro_embarque, tipo_carro, cliente_telefone, sexo, fila_, lon=lon, lat=lat) 

    print(motorista)
    # Verifica as cordenadas do destino
    cordenadas = BotQuerys().lat_lon_destino(bairro_destino)
    if cordenadas:
        lat_destino = cordenadas['latitude']
        lon_destino = cordenadas['longitude']
        tipo_destino = cordenadas['tipo_destino']

    # Valores da distancia e duração da corrida ate o destino
    valores = distancia_destino(api_key, lon_destino, lat_destino, lon=lon, lat=lat) 

    # busca no banco o tipo do bairro
    tipo_bairro =  BotQuerys().tipo_bairro_embarque(bairro_embarque)

    # tratamento do JSON para instring
    if isinstance(motorista, str):
        motorista = json.loads(motorista)  
    else:
        motorista = motorista
    
    # Se for troca retorna o status livre do motorista a pos a busca de um motorista na fila
    if tel_motorista:
        BotQuerys().trocar_status_mot(tel_motorista)
    
    # Se nao tem motorista disponivel enviar requisição para o Botconversa
    if motorista == None:
        enviar_corrida_bot_None(cliente_telefone)
        return jsonify({"mensagem": "Nenhum motorista disponível no momento."}), 200
    
    # tratando os dados que vem das funçoes
    duracao_corrida = valores['duracao'] 
    tempo_para_embarque = motorista['tempo_para_embarque'] 
    duracao_corrida_int = int(duracao_corrida)
    tempo_para_embarque_int = int(tempo_para_embarque)
    telefone = motorista['telefone']
    tempo_total = duracao_corrida_int + tempo_para_embarque_int 
    tempo_total = str(tempo_total)

    # Enviar dados para o Botconversa
    enviar_corrida_bot(motorista, tipo_carro, sexo, valores, cliente_telefone, tipo_destino, tipo_bairro, bairro_embarque, bairro_destino, embarque) 
    # enviar os dados do motorista para o cliente
    enviar_mot_cliente(motorista, valores, cliente_telefone, tipo_destino, tipo_bairro) 
    # iNICIAR a corrida no banco de dados
    BotQuerys().iniciar_corrida(telefone, bairro_destino, tempo_total)
 
    return jsonify({"motorista_proximo": motorista }), 200
   
@public_endpoint
@botconversa_app.route('/cadastrar', methods=['POST'])
def cadastra_motorista():
    ''' Cadastra um motorista no sistema '''
    
    data_json = request.get_json()
    telefone = data_json['telefone']
    tipo_carro = data_json['tipo_carro']
    name = data_json['name']
    sexo = data_json['sexo']

    BotQuerys().cadastrar_motorista(name, sexo, telefone, tipo_carro)

    return jsonify({"response": data_json}), 200

@public_endpoint
@botconversa_app.route('/cancelar_corrida', methods=['POST'])
def cancelar():
    ''' Recebe os dados do cancelamento
        telefone_motorista '''
    
    data_json = request.get_json()
    mot_telefone = data_json['mot_telefone'] 
    BotQuerys.cancelar_corrida(mot_telefone)

    return jsonify({'Cancelado': data_json})

@public_endpoint
@botconversa_app.route('/desbloquear', methods=['POST'])
def desbloquear():
    ''' Recebe os dados do desbloqueio do motorista '''
   
    data_json = request.get_json()
   
    cliente_telefone = data_json['cliente_telefone'] 
    mot_telefone = data_json['mot_telefone']
    BotQuerys.desbloquear_mot(mot_telefone, cliente_telefone)

    return jsonify({'Desbloqueado': data_json})

@public_endpoint
@botconversa_app.route('/em_off', methods=['POST'])
def em_off():
    ''' Deixar o motorista em status off '''
    
    data_json = request.get_json()
    print(data_json)
    mot_telefone = data_json['mot_telefone'] 
    print(mot_telefone)
    BotQuerys.entrar_off(mot_telefone) 
  

    return jsonify({"response": data_json}), 200

@public_endpoint
@botconversa_app.route('/bloquear', methods=['POST'])
def bloquear():
    ''' Enviar o telefone do cliente para bloquear
        o motorista '''
    
    data_json = request.get_json() 

    cliente_telefone = data_json['cliente_telefone'] 
    mot_telefone = data_json['mot_telefone']

    BotQuerys().bloquear_motorista( mot_telefone, cliente_telefone)

    return jsonify({"response": mot_telefone}), 200


@public_endpoint
@botconversa_app.route('/desfavoritar', methods=['POST'])
def desfavoritar():
    ''' Enviar o telefone do cliente para remover
        dos favoritos do motorista '''
    
    data_json = request.get_json() 
  
    cliente_telefone = data_json['cliente_telefone'] 
    mot_telefone = data_json['mot_telefone']

    BotQuerys().remov_favorito(mot_telefone, cliente_telefone)

    return jsonify({"response": data_json}), 200


@public_endpoint
@botconversa_app.route('/favoritar', methods=['POST'])
def favoritar():
    ''' Enviar o telefone do cliente para bloquear
        o motorista '''
    
    data_json = request.get_json() 
   
    cliente_telefone = data_json['cliente_telefone'] 
    mot_telefone = data_json['mot_telefone']

    BotQuerys().adiciona_favorito(mot_telefone, cliente_telefone)

    return jsonify({"response": mot_telefone}), 200 

@public_endpoint
@botconversa_app.route('/avaliacao', methods=['POST'])
def avaliacao():
    ''' Enviar o telefone do motorista a nota e a avaliação do motorista '''
    
    data_json = request.get_json() 
  
    nota = data_json['nota'] 
    mot_telefone = data_json['mot_telefone']

    BotQuerys().adicionar_avaliacao(mot_telefone, nota)

    return jsonify({"response": mot_telefone}), 200 


@public_endpoint
@botconversa_app.route('/referencia', methods=['POST'])
def referecia():
    ''' referencia de localização ''' 

    data_json = request.get_json() 
  
    referencia = data_json['referencia'] 
    mot_telefone = data_json['mot_telefone'] 
    BotQuerys().referecia(mot_telefone, referencia) 

    return jsonify({"response": mot_telefone}), 200