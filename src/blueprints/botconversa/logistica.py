from datetime import datetime
from fuzzywuzzy import process
import requests
import json
from .bairros import bairros

import time


def corrigir_bairro(bairro_digitado):

    # Criar uma lista de possíveis nomes (principais e alternativos)
    todos_nomes = []
    nome_para_bairro = {}

    for bairro, dados in bairros.items():
        # Adicionar o nome principal do bairro
        todos_nomes.append(bairro)
        nome_para_bairro[bairro] = bairro

        # Adicionar nomes alternativos
        for nome_alternativo in dados['nomes_alternativos']:
            todos_nomes.append(nome_alternativo)
            nome_para_bairro[nome_alternativo] = bairro
    nome_corrigido, _ = process.extractOne(bairro_digitado, todos_nomes)


    return nome_para_bairro[nome_corrigido]

def selecionar_motorista(fila, bairro_cliente):
    bairro_cliente_corrigido = corrigir_bairro(bairro_cliente)
    
    motoristas_disponiveis = [motorista for motorista in fila if motorista['bairro_atual'] == bairro_cliente_corrigido]

    if len(motoristas_disponiveis) > 1:
        motoristas_disponiveis.sort(key=lambda m: m['data_entrada'])
    
    if motoristas_disponiveis:
        return motoristas_disponiveis[0]['telefone']

    return "Sem motoristas disponíveis"

def busca_motorista(api_key, bairro_embarque, tipo_carro, cliente_telefone, sexo, fila_, lat, lon):
    '''Busca o motorista mais próximo com base em verificações e tempo livre, priorizando motoristas no mesmo bairro.'''

    motorista_mais_proximo = None
    menor_distancia = float('inf')  
    motorista_com_maior_tempo_livre = None
    maior_tempo_livre = float('-inf')
    tempo_para_embarque = None

    # Filtrar motoristas disponíveis e válidos
    for motorista in fila_:
        motorista_sexo = motorista[1] 
        mot_tipo_carro = motorista[2]
     
     
        motorista_status = motorista[8] 
        motorista_cliente_bloqueado = motorista[9]
        motorista_hora_livre = motorista[10] 

        # Verificar se o cliente está bloqueado para o motorista
        clientes_bloqueados = []
        if isinstance(motorista_cliente_bloqueado, str):
            try:
                cliente_bloqueado_dict = json.loads(motorista_cliente_bloqueado)
                if "cliente" in cliente_bloqueado_dict:
                    clientes_bloqueados = cliente_bloqueado_dict["cliente"]
            except json.JSONDecodeError:
                print(f"Erro ao decodificar JSON de cliente_bloqueado para o motorista {motorista[5]}")
        elif isinstance(motorista_cliente_bloqueado, dict):
            if "cliente" in motorista_cliente_bloqueado:
                clientes_bloqueados = motorista_cliente_bloqueado["cliente"]

        if cliente_telefone in clientes_bloqueados:
            print(f"Cliente {cliente_telefone} está bloqueado para o motorista {motorista[5]}")
            continue

        # Filtrar motoristas livres, com sexo e tipo de carro desejado
        if motorista_status == "livre" and (sexo == 'neutro' or motorista_sexo == sexo) and (tipo_carro == 'nenhum' or mot_tipo_carro == tipo_carro):
            # Verificar a distância e o tempo livre do motorista
            motorista_lat = motorista[3]
            motorista_lon = motorista[4]

            # URL da API de cálculo de rotas
            url = f'https://us1.locationiq.com/v1/directions/driving/{motorista_lon},{motorista_lat};{lon},{lat}?key={api_key}&steps=true&alternatives=true&geometries=polyline&overview=full'

            try:
                response = requests.get(url)

                if response.status_code == 200:
                    dados = response.json()

                    # Extrair a distância e o tempo estimado de chegada
                    distancia = dados['routes'][0]['distance']
                    tempo_para_embarque_atual = dados['routes'][0]['duration']

                    # Calcular o tempo livre do motorista
                    if isinstance(motorista_hora_livre, datetime):
                        tempo_livre = (datetime.now() - motorista_hora_livre).total_seconds()
                    else:
                        print(f"Formato de hora inválido para o motorista {motorista[5]}")
                        continue

                    # Atualizar o motorista com maior tempo livre
                    if tempo_livre > maior_tempo_livre:
                        maior_tempo_livre = tempo_livre
                        motorista_com_maior_tempo_livre = motorista

                    # Verificar se o motorista está mais próximo
                    if distancia < menor_distancia:
                        menor_distancia = distancia
                        motorista_mais_proximo = motorista
                        tempo_para_embarque = tempo_para_embarque_atual

                    # Se a distância está dentro de 5% da menor distância, considerar também o motorista atual
                    elif (abs(distancia - menor_distancia) / menor_distancia) <= 0.05:
                        # Comparar o tempo livre
                        if tempo_livre > maior_tempo_livre:
                            motorista_mais_proximo = motorista
                            maior_tempo_livre = tempo_livre
                            tempo_para_embarque = tempo_para_embarque_atual

                else:
                    print(f"Erro na requisição: {response.status_code}")
            except Exception as e:
                print(f"Ocorreu um erro: {e}")

            # Aguardar 0,5 segundos para não sobrecarregar a API
            time.sleep(0.3)

    # Verificar se encontrou um motorista
    if motorista_mais_proximo:
        resultado = {
            'id': motorista_mais_proximo[0],
            'sexo': motorista_mais_proximo[1],
            'tipo_carro': motorista_mais_proximo[2],
            'latitude': motorista_mais_proximo[3],
            'longitude': motorista_mais_proximo[4],
            'name': motorista_mais_proximo[5],
            'telefone': motorista_mais_proximo[6],
            'bairro': motorista_mais_proximo[7],
            'distancia_metros': menor_distancia,
            'tempo_para_embarque': tempo_para_embarque
        }
        return resultado

    return None

def enviar_corrida_bot_None(cliente_telefone):
    ''' Se nao tiver Nenhum motorista disponivel retorna para o Bot '''
    
    api_url = 'https://backend.botconversa.com.br/api/v1/webhooks-automation/catch/87780/fRfF7k8rAZrh/'
    key = '26084536-20e3-4c12-98fc-dd6b30ba2417'

    params = {
        'cliente_telefone': cliente_telefone 
    }

    headers = {
        'Authorization': f'API-KEY {key}',
        'Content-Type': 'application/json'
    }

    response = requests.post(api_url, json=params, headers=headers, timeout=30)

    if response.status_code == 200:
        print("Requisição enviada ao bot com sucesso!")
    else:
        print(f"Erro ao enviar requisição ao bot: {response.status_code}")
        print(response.text)

def enviar_mot_cliente(motorista, valores, cliente_telefone, tipo_destino, tipo_bairro):
    ''' enviar informaçoês do motorista para o cliente '''
    
    distancia = valores['distancia']
    duracao = valores['duracao'] 


    api_url = 'https://backend.botconversa.com.br/api/v1/webhooks-automation/catch/87780/EmDfsDrCgLMH/'
    key = '26084536-20e3-4c12-98fc-dd6b30ba2417'

    if isinstance(motorista, str):
        # Se for, converte a string JSON para um dicionário
        motorista = json.loads(motorista)

    telefone = motorista["telefone"]
    sexo = motorista['sexo']
    tipo_carro = motorista['tipo_carro']

    params = {
        'sexo':sexo,
        'tipo_carro':tipo_carro,
        'mot_telefone':telefone,
        'cliente_telefone': cliente_telefone,
        'distancia':distancia,
        'duracao':duracao,
        'tipo_destino':tipo_destino,
        'tipo_embarque':tipo_bairro
    }
    headers = {
        'Authorization': f'API-KEY {key}', 
        'Content-Type': 'application/json'  
    }
    response = requests.post(api_url, json=params, headers=headers, timeout=30)

    # Verificando e imprimindo o resultado
    if response.status_code == 200:
        print("Requisição bem-sucedida para cliente!")
     
    else:
        print(f"Erro na requisição: {response.status_code}")
        print(response.text)

    return response.text

def enviar_corrida_bot(motorista, tipo_carro, sexo, valores, cliente_telefone, tipo_destino, tipo_bairro, bairro_embarque, bairro_destino, embarque):
    ''' Embarque
        Telefone do motorista
        Duração total 
        distancia
        Bairro embarque '''
    
    api_url = 'https://backend.botconversa.com.br/api/v1/webhooks-automation/catch/87780/FTD5inieIqwk/'
    key = '26084536-20e3-4c12-98fc-dd6b30ba2417' 
    if isinstance(motorista, str):
        # Se for, converte a string JSON para um dicionário
        motorista = json.loads(motorista)

    distancia = valores['distancia']
    duracao = valores['duracao'] 
    telefone = motorista["telefone"]
    mot_sexo = motorista['sexo']
    mot_tipocarro = motorista['tipo_carro']
 
    params = {
        'bairro_embarque':bairro_embarque,
        'bairro_destino':bairro_destino,
        'sexo':mot_sexo,
        'prefere_sexo': sexo,
        'prefere_carro': tipo_carro,
        'tipo_carro':mot_tipocarro,
        'embarque':embarque,
        'telefone':telefone,
        'cliente_telefone': cliente_telefone,
        'distancia':distancia,
        'duracao':duracao,
        'tipo_destino':tipo_destino,
        'tipo_embarque':tipo_bairro
    }
    headers = {
        'Authorization': f'API-KEY {key}', 
        'Content-Type': 'application/json'  # Definindo o tipo de conteúdo
    }
    response = requests.post(api_url, json=params, headers=headers, timeout=30)

    # Verificando e imprimindo o resultado
    if response.status_code == 200:
        print("Requisição bem-sucedida para o bot")
     
    else:
        print(f"Erro na requisição: {response.status_code}")
        print(response.text)

    return response.text

def distancia_destino(api_key, lon_destino, lat_destino, lat, lon,):
    ''' Busca a distancia do destino do Cliente '''

    # Montar a URL da requisição
    url = f'https://us1.locationiq.com/v1/directions/driving/{lon_destino},{lat_destino};{lon},{lat}?key={api_key}&steps=true&alternatives=true&geometries=polyline&overview=full'

    # Fazer a requisição GET para a API de rotas
    response = requests.get(url)

    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:
        dados = response.json()
       
        duracao = dados['routes'][0]['duration']  
        distancia = dados['routes'][0]['distance']

        return {
            'distancia': distancia,  
            'duracao': duracao,   
        }
    else:
        # Caso ocorra um erro na requisição, retornar uma mensagem de erro
        return {
            'erro': 'Não foi possível obter os dados da API.',
            'status_code': response.status_code
        }

def lat_lon_cliente(api_key, embarque, bairro_embarque, cidade):
    ''' Função para buscar a latitude e longitude do cliente '''

    # Construir a URL da API para buscar a latitude e longitude
    url = f'https://us1.locationiq.com/v1/search?key={api_key}&q={embarque},{bairro_embarque},{cidade}&format=json'

    try:
        # Fazer a requisição GET para a API
        response = requests.get(url)

        # Verificar se a requisição foi bem-sucedida
        if response.status_code == 200:
            data = response.json()
            
            # Extrair lat e lon da primeira resposta
            if isinstance(data, list) and len(data) > 0:
                display_name = data[0]['display_name']
                lat = data[0]['lat']
                lon = data[0]['lon']
                print(display_name)
                # Retornar as coordenadas como um dicionário
                return {
                    'latitude': lat,
                    'longitude': lon
                }
               
            else:
                print("Nenhuma coordenada encontrada na resposta.")
                return None

        else:
            print(f"Erro na requisição: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return None
