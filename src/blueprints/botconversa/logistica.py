from datetime import datetime
from fuzzywuzzy import process
import requests
import json
from .bairros import bairros

import time


api_key = 'pk.f17234d51a1015ab3c5ecb138de627c9' 


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


def busca_motorista(api_key, sexo, fila_, lat, lon):
    '''Logística para buscar o motorista mais próximo do cliente'''

    motorista_mais_proximo = None
    menor_distancia = float('inf')  

    # Percorrer cada motorista na lista
    for motorista in fila_:
        motorista_sexo = motorista[1]
        motorista_status = motorista[8]  # Supondo que o status esteja na posição 8

        # Filtrar motoristas que estejam "livres" e com o sexo correspondente
        if motorista_status == "livre" and (sexo == 'neutro' or motorista_sexo == sexo):
            motorista_lat = motorista[3] 
            motorista_lon = motorista[4]  

            # URL da API de cálculo de rotas
            url = f'https://us1.locationiq.com/v1/directions/driving/{motorista_lon},{motorista_lat};{lon},{lat}?key={api_key}&steps=true&alternatives=true&geometries=polyline&overview=full'

            try:
                response = requests.get(url)

                if response.status_code == 200:
                    dados = response.json()

                    # Extrair a distância da resposta (primeira rota)
                    distancia = dados['routes'][0]['distance'] 
                    tempo_para_embarque = dados['routes'][0]['duration']

                    # Se a distância atual for menor que a menor distância registrada
                    if distancia < menor_distancia:
                        menor_distancia = distancia
                        motorista_mais_proximo = motorista  
                else:
                    print(f"Erro na requisição: {response.status_code}")
            except Exception as e:
                print(f"Ocorreu um erro: {e}")

            # Aguardar 0,5 segundos antes de tentar a próxima requisição
            time.sleep(0.5)

    # Caso encontre um motorista
    if motorista_mais_proximo:
        resultado = {
            'id': motorista_mais_proximo[0],            # ID do motorista
            'sexo': motorista_mais_proximo[1],          # Sexo
            'tipo_carro': motorista_mais_proximo[2],    # Tipo do carro
            'latitude': motorista_mais_proximo[3],      # Latitude
            'longitude': motorista_mais_proximo[4],     # Longitude
            'name': motorista_mais_proximo[5],          # Nome
            'telefone': motorista_mais_proximo[6],      # Telefone
            'bairro': motorista_mais_proximo[7],        # Bairro
            'distancia_metros': menor_distancia,        # Distância até o cliente
            'tempo_para_embarque': tempo_para_embarque  # Tempo estimado de chegada
        }
        return json.dumps(resultado, indent=4)
    
    else:
        # Se não encontrar motorista, envia uma requisição ao bot
        api_url = 'https://backend.botconversa.com.br/api/v1/webhooks-automation/catch/87780/FTD5inieIqwk/'
        key = '26084536-20e3-4c12-98fc-dd6b30ba2417'
        
        params = {
            'id': 'nenhum id',
            'sexo': sexo,
            'tipo_carro': 'desconhecido',                   # Pode substituir ou deixar como "desconhecido"
            'lat': 'nenhum',
            'lon': 'nenhum',
            'name': 'nenhum',
            'telefone': '00000000000',                      # Telefone desconhecido
            'bairro': 'Nenhum',           
            'distancia': 'Desconhecida',                    # Distância não calculada
            'tipo_destino': 'Desconhecido',                 # Substitua se necessário
            'tipo_embarque': 'Desconhecido',                # Substitua se necessário
            'tempo_para_embarque': 'Nenhum'
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
            return  
        
        # Retorna a mensagem indicando a falta de motoristas
        return json.dumps({
            'mensagem': f"Nenhum motorista {'masculino' if sexo == 'masculino' else 'feminino' if sexo == 'feminino' else ''} disponível com status 'livre'."
        }, indent=4)
    


    
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
        'Content-Type': 'application/json'  # Definindo o tipo de conteúdo
    }
    response = requests.post(api_url, json=params, headers=headers, timeout=30)

    # Verificando e imprimindo o resultado
    if response.status_code == 200:
        print("Requisição bem-sucedida!")
     
    else:
        print(f"Erro na requisição: {response.status_code}")
        print(response.text)

    return response.text



def enviar_corrida_bot(motorista, valores, cliente_telefone, tipo_destino, tipo_bairro, bairro_embarque, bairro_destino, embarque):
    ''' Embarque
        Telefone do motorista
        Duração total 
        distancia
        Bairro embarque '''
    
    distancia = valores['distancia']
    duracao = valores['duracao'] 


    api_url = 'https://backend.botconversa.com.br/api/v1/webhooks-automation/catch/87780/FTD5inieIqwk/'
    key = '26084536-20e3-4c12-98fc-dd6b30ba2417' 
    if isinstance(motorista, str):
        # Se for, converte a string JSON para um dicionário
        motorista = json.loads(motorista)

    telefone = motorista["telefone"]
    sexo = motorista['sexo']
    tipo_carro = motorista['tipo_carro']
 
    params = {
        'bairro_embarque':bairro_embarque,
        'bairro_destino':bairro_destino,
        'sexo':sexo,
        'tipo_carro':tipo_carro,
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
        print("Requisição bem-sucedida!")
     
    else:
        print(f"Erro na requisição: {response.status_code}")
        print(response.text)

    return response.text


def distancia_destino(api_key, lon_destino, lat_destino, lon, lat):
    # Montar a URL da requisição
    # print(f'Cliente {lon}  {lat} ')
    # print(f'Destino {lon_destino} {lat_destino}')
    
    url = f'https://us1.locationiq.com/v1/directions/driving/{lon_destino},{lat_destino};{lat},{lon}?key={api_key}&steps=true&alternatives=true&geometries=polyline&overview=full'

    # Fazer a requisição GET para a API de rotas
    response = requests.get(url)

    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:
        dados = response.json()
       
        duracao = dados['routes'][0]['duration']  
        distancia = dados['routes'][0]['distance']
        # print(duracao)
        # print(distancia)

        # Retornar os dados necessários
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
            # Obter o JSON da resposta
            data = response.json()

            
            # Extrair lat e lon da primeira resposta
            if isinstance(data, list) and len(data) > 0:
                display_name = data[0]['display_name']
                lat = data[0]['lat']
                lon = data[0]['lon']
                # print(f'Endereço {display_name}')
                # print(f"Localização do cliente: Latitude: {lat}, Longitude: {lon}")

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
