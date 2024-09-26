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


def busca_motorista(api_key, fila_, lat, lon):
    ''' Logistica para busca o motorista mas proximo do cliente '''

    motorista_mais_proximo = None
    menor_distancia = float('inf')  

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
                distancia = dados['routes'][0]['distance'] 
              
                # print(f"Distância entre motorista {motorista[3]} e cliente: {distancia} metros")
                # Se a distância atual for menor que a menor distância registrada
                if distancia < menor_distancia:
                    menor_distancia = distancia
                    motorista_mais_proximo = motorista  
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
        

    return json.dumps(resultado, indent=4)
    

def enviar_corrida_bot(motorista, valores, tipo_destino, tipo_bairro, bairro_embarque, embarque):
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

    telefone = motorista["motorista_mais_proximo"]["telefone"]
    print(telefone)
    # Parâmetros da requisição
    params = {
        'bairro_embarque':bairro_embarque,
        'embarque':embarque,
        'telefone':telefone,
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



def atualizar_tarifas(dados):
    tarifas["bandeira_1"]["valor_minimo"] = float(dados.get('valor_minimo_b1', tarifas["bandeira_1"]["valor_minimo"]))
    tarifas["bandeira_1"]["valor_por_km"] = float(dados.get('valor_por_km_b1', tarifas["bandeira_1"]["valor_por_km"]))
    tarifas["bandeira_1"]["valor_por_minuto"] = float(dados.get('valor_por_minuto_b1', tarifas["bandeira_1"]["valor_por_minuto"]))

    tarifas["bandeira_2"]["valor_minimo"] = float(dados.get('valor_minimo_b2', tarifas["bandeira_2"]["valor_minimo"]))
    tarifas["bandeira_2"]["valor_por_km"] = float(dados.get('valor_por_km_b2', tarifas["bandeira_2"]["valor_por_km"]))
    tarifas["bandeira_2"]["valor_por_minuto"] = float(dados.get('valor_por_minuto_b2', tarifas["bandeira_2"]["valor_por_minuto"]))

    return json.dumps(tarifas)


def calcular_valor_corrida(valores):
    distancia = valores['distancia']
    duracao = valores['duracao'] 
    horario = valores['horario_solicitacao']
   
    # Converter distâncias de metros para quilômetros
    distancia_total_km = distancia / 1000
    duracao_total_min = duracao / 60 

    # Definir bandeira e valores mínimos com base no horário
    hora_solicitacao = type(int[horario])
    print(hora_solicitacao)
    # Verificar se a corrida será durante o dia ou madrugada
    if hora_solicitacao >= 0 and hora_solicitacao < 6:
        # Bandeira 2 (madrugada)
        bandeira = 2
        valor_minimo = tarifas["bandeira_2"]["valor_minimo"]
        valor_por_km = tarifas["bandeira_2"]["valor_por_km"]
        valor_por_minuto = tarifas["bandeira_2"]["valor_por_minuto"]
    else:
        # Bandeira 1 (dia)
        bandeira = 1
        valor_minimo = tarifas["bandeira_1"]["valor_minimo"]
        valor_por_km = tarifas["bandeira_1"]["valor_por_km"]
        valor_por_minuto = tarifas["bandeira_1"]["valor_por_minuto"]
    
    # Cálculo do valor da corrida
    valor_corrida = (valor_por_km * distancia_total_km) + (valor_por_minuto * duracao_total_min)
    valor_total = max(valor_corrida, valor_minimo)
    
    return {
        "distancia_total_km": distancia_total_km,
        "tempo_total_minutos": duracao_total_min,
        "bandeira": bandeira,
        "valor_total": round(valor_total, 2)  # Arredondar para duas casas decimais
    }
