from datetime import datetime
from fuzzywuzzy import process
import requests
import json

from .bairros import bairros

api_key = 'pk.f17234d51a1015ab3c5ecb138de627c9' 

# Corrigir possíveis erros ortográficos dos bairros
def corrigir_bairro(bairro_digitado):
    todos_bairros = list(bairros.keys())
    bairro_corrigido, _ = process.extractOne(bairro_digitado, todos_bairros)
    return bairro_corrigido

# Adicionar motorista na fila com a data e hora atual
def adicionar_motorista_na_fila(nome, bairro_atual, telefone):
    data_entrada = datetime.now()
    MotoristsQuerys.new(nome, {
        "bairro_atual": bairro_atual,
        "telefone": telefone,
        "data_entrada": data_entrada
    })

# Função para selecionar o motorista mais próximo ou a mais tempo na fila
def selecionar_motorista(fila, bairro_cliente):
    bairro_cliente_corrigido = corrigir_bairro(bairro_cliente)
    
    motoristas_disponiveis = [motorista for motorista in fila if motorista['bairro_atual'] == bairro_cliente_corrigido]

    if len(motoristas_disponiveis) > 1:
        motoristas_disponiveis.sort(key=lambda m: m['data_entrada'])
    
    if motoristas_disponiveis:
        return motoristas_disponiveis[0]['telefone']

    return "Sem motoristas disponíveis"

# Função para obter a distância entre dois bairros usando a API LocationIQ
def obter_distancia(api_key, endereco_origem, endereco_destino):
    url = "https://us1.locationiq.com/v1/directions/driving/"
    params = {
        "key": api_key,
        "origin": endereco_origem,
        "destination": endereco_destino,
        "format": "json"
    }
    response = requests.get(url, params=params)
    dados = response.json()
    distancia = dados['routes'][0]['distance']  # Distância em metros
    return distancia