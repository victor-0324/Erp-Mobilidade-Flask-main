from datetime import datetime
from fuzzywuzzy import process
import requests
import json
from .bairros import bairros
import time

from .bairros import bairros
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


def logistica(api_key, fila_, lat, lon, bairro_embarque, embarque):
    ''' Logistica para busca o motorista mas proximo do cliente '''

    motorista_mais_proximo = None
    menor_distancia = float('inf')  # Iniciando com uma distância infinita

    # Percorrer cada motorista na lista
    for motorista in fila_:
        motorista_lat = motorista[1]  # Latitude do motorista
        motorista_lon = motorista[2]  # Longitude do motorista

        # Formatar a URL da requisição
        url = f'https://us1.locationiq.com/v1/directions/driving/{motorista_lon},{motorista_lat};{lon},{lat}?key={api_key}&steps=true&alternatives=true&geometries=polyline&overview=full'

        try:
            # Fazer a requisição GET para a API de rotas
            response = requests.get(url)

            # Verificar se a requisição foi bem-sucedida
            if response.status_code == 200:
                dados = response.json()
                
                # Extrair a distância da resposta (primeira rota)
                distancia = dados['routes'][0]['distance']  # Distância em metros

                print(f"Distância entre motorista {motorista[3]} e cliente: {distancia} metros")

                # Se a distância atual for menor que a menor distância registrada
                if distancia < menor_distancia:
                    menor_distancia = distancia
                    motorista_mais_proximo = motorista  # Atualiza o motorista mais próximo
            else:
                print(f"Erro na requisição: {response.status_code}")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
        # Esperar 0,5 segundos antes da próxima requisição
        time.sleep(1)

    # Retornar o motorista mais próximo e a distância em JSON
    if motorista_mais_proximo:
        resultado = {
            'motorista_mais_proximo': {
                'id': motorista_mais_proximo[0],        # ID do motorista
                'latitude': motorista_mais_proximo[1],  # Latitude
                'longitude': motorista_mais_proximo[2], # Longitude
                'name': motorista_mais_proximo[3],      # Nome
                'telefone': motorista_mais_proximo[4],  # Telefone
                'bairro': motorista_mais_proximo[5],    # Bairro
                'distancia_metros': menor_distancia     # Distância mais curta
            }
        }
    else:
        resultado = {
            'mensagem': "Nenhum motorista encontrado."
        }

    
    api_url = 'https://backend.botconversa.com.br/api/v1/webhooks-automation/catch/87780/FTD5inieIqwk/'
    key = '26084536-20e3-4c12-98fc-dd6b30ba2417' 

    telefone = resultado['motorista_mais_proximo']['telefone']
     
    # Parâmetros da requisição
    params = {
        'bairro_embarque': bairro_embarque,
        'embarque': embarque,
        'telefone':telefone 
    }

    # Headers com a chave de autenticação
    headers = {
        'Authorization': f'API-KEY {key}', 
        'Content-Type': 'application/json'  # Definindo o tipo de conteúdo
    }

    # Fazendo a requisição POST
    response = requests.post(api_url, json=params, headers=headers, timeout=30)

    # Verificando e imprimindo o resultado
    if response.status_code == 200:
        print("Requisição bem-sucedida!")
     
    else:
        print(f"Erro na requisição: {response.status_code}")
        print(response.text)

    return json.dumps(resultado, indent=4)
    

def busca_lat_lon(api_key, embarque, bairro_embarque, cidade):
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
                print(f'Endereço {display_name}')
                print(f"Localização do cliente: Latitude: {lat}, Longitude: {lon}")

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




# Carregar o JSON de um arquivo
    # with open('src/blueprints/botconversa/bairros_proximos.json', 'r') as file:
    #     bairros_proximos = json.load(file)

  
    # bairro_embarque_cliente = cliente
    
    # bairro_corrigido = corrigir_bairro(bairro_embarque_cliente)
    # print(bairro_embarque_cliente)
    # print(bairro_corrigido)

    
    # # # Buscar proximidades do bairro de embarque do cliente
    # proximidades = bairros_proximos.get('bairros_proximos', {}).get(bairro_corrigido, None)
    # if not proximidades:
    #     return "Bairro de embarque do cliente não encontrado nas proximidades."

    # perto = proximidades["perto"]
    # medio = proximidades["medio"]
    # longe = proximidades["longe"]

    # motoristas_perto = []
    # motoristas_medio = []
    # motoristas_longe = []

    # # Verificar cada motorista na fila
    # for motorista in fila:
    #     bairro_motorista = motorista[0]
    #     telefone_motorista = motorista[1]

    #     if bairro_motorista in perto:
    #         motoristas_perto.append((bairro_motorista, telefone_motorista))
    #     elif bairro_motorista in medio:
    #         motoristas_medio.append((bairro_motorista, telefone_motorista))
    #     elif bairro_motorista in longe:
    #         motoristas_longe.append((bairro_motorista, telefone_motorista))

    # # Retornar o motorista mais próximo disponível
    # if motoristas_perto:
    #     return f"Motorista mais próximo: {motoristas_perto[0][1]} no bairro {motoristas_perto[0][0]}"
    # elif motoristas_medio:
    #     return f"Motorista a distância média: {motoristas_medio[0][1]} no bairro {motoristas_medio[0][0]}"
    # elif motoristas_longe:
    #     return f"Motorista mais distante: {motoristas_longe[0][1]} no bairro {motoristas_longe[0][0]}"
    # else:
    #     return "Nenhum motorista disponível." 