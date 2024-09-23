# pylint: disable=too-few-public-methods, consider-using-f-string
"""User Querys"""

from src.database.db_connection import db_connector
from .models import DriverQueue
from math import radians
from sqlalchemy import func, Float
from .bairros import bairros
import requests


class BotQuerys:
    """A Consult if name alredy exits"""
    @classmethod
    @db_connector
    def fila(cls, connection):
        """Return all motorists in database"""
        return connection.session.query(DriverQueue).all()

    @classmethod
    @db_connector
    def novo(cls, connection, name, telefone, bairro):
        """Função para adicionar novo driver na fila ou atualizar localização"""

        # Verificar se o nome já existe no banco de dados
        check_name = connection.session.query(DriverQueue).filter_by(name=name).first()

        # Verificar se o bairro enviado está no dicionário de bairros
        if bairro in bairros:
            # Pegar latitude e longitude do bairro
            lat = bairros[bairro]["lat"]
            lon = bairros[bairro]["lon"]
        else:
            print(f"Bairro {bairro} não encontrado.")
            return None  # Ou lidar com o caso de bairro não encontrado de outra forma

        if check_name:
            # Se o nome já existe, atualizar lat e lon
            print(f"Motorista {name} já existe. Atualizando localização para o bairro {bairro}.")
            check_name.lat = lat
            check_name.lon = lon
            check_name.bairro = bairro  # Opcionalmente, atualizar o bairro também

            # Salvar as atualizações no banco de dados
            connection.session.commit()
            return check_name

        # Se o nome não existir, criar um novo registro
        new_driver = DriverQueue(name=name, telefone=telefone, bairro=bairro, lat=lat, lon=lon)
        connection.session.add(new_driver)
        connection.session.commit()

        print(f"Novo motorista {name} adicionado com localização: {lat}, {lon}")
        return new_driver

    @classmethod
    @db_connector
    def remove_first_driver(cls, connection, telefone):
        """Remove the first driver in the queue and return its data"""
        first_driver = connection.session.query(DriverQueue).filter_by(telefone=telefone).first()
        if first_driver:
            first_driver_data = {
                'name': first_driver.name,
                'telefone': first_driver.telefone,
                'bairro': first_driver.bairro
            }
            connection.session.delete(first_driver)
            connection.session.commit()
            return first_driver_data
        else:
            return None

    @classmethod
    @db_connector
    def sair_da_fila(cls, connection, telefone):
        """someting"""
        check_name = connection.session.query(DriverQueue).filter_by(telefone=telefone).first()
        if check_name != None:  # pylint: disable=singleton-comparison
            connection.session.delete(check_name)
            connection.session.commit()

    @classmethod
    @db_connector
    def motorista_da_vez(cls, connection, bairro):
        """Seleciona e remove o motorista que está há mais tempo na fila em um determinado bairro"""
        motorista = connection.session.query(DriverQueue)\
            .filter_by(bairro=bairro)\
            .order_by(DriverQueue.data_entrada.asc())\
            .first()
        
        if motorista is not None:  # Verifica se há algum motorista na fila
            connection.session.delete(motorista)
            connection.session.commit()
            return motorista
        
        return None  # Caso não haja motoristas no bairro especificado
    

    @classmethod
    @db_connector
    def calcular_motorista_mais_proximo(cls, connection, input_lat, input_lon):
        # Conversão de string para float para cálculo
        input_lat = float(input_lat) 
        input_lon = float(input_lon)

        R = 6371  # Raio da Terra em km

        motorista_proximo = (
            connection.session.query(DriverQueue,
                # Cálculo da distância usando a fórmula de Haversine
                (R * func.acos(
                    func.cos(func.radians(input_lat)) * func.cos(func.radians(func.cast(DriverQueue.lat, Float))) *
                    func.cos(func.radians(func.cast(DriverQueue.lon, Float)) - func.radians(input_lon)) +
                    func.sin(func.radians(input_lat)) * func.sin(func.radians(func.cast(DriverQueue.lat, Float)))
                )).label('distancia')
            )
            .order_by('distancia')  # Ordena pela distância mais próxima
            .first()  # Retorna o motorista mais próximo
        )

        return motorista_proximo