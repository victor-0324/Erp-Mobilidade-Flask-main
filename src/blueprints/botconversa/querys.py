# pylint: disable=too-few-public-methods, consider-using-f-string
"""User Querys"""

from sqlalchemy import or_
from src.database.db_connection import db_connector
from .models import DriverQueue, Bairros
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
    def usar_bairro(cls, connection):
        for nome_bairro, info_bairro in bairros.items():
            novo_bairro = Bairros(
                nome_bairro=nome_bairro,
                tipo_bairro=info_bairro['tipo_de_bairro'][0],  
                nome_alternativo=', '.join(info_bairro['nomes_alternativos']), 
                lat=str(info_bairro['lat']),
                lon=str(info_bairro['lon']),
                cidade= 'São Lourenço MG',
                cep =  '37470000'
            )
            connection.session.add(novo_bairro)
        connection.session.commit()
        connection.session.close()


    @classmethod
    @db_connector
    def novo(cls, connection, name, telefone, bairro_nome):
        """Função para adicionar novo motorista ou atualizar localização"""

        check_name = connection.session.query(DriverQueue).filter_by(name=name).first()
        bairro = connection.session.query(Bairros).filter_by(nome_bairro=bairro_nome).first()

        if bairro:
            lat = bairro.lat
            lon = bairro.lon
        else:
            print(f"Bairro {bairro_nome} não encontrado no banco de dados.")
            return None

        # Se o nome já existe, atualizar lat e lon
        if check_name:
            print(f"Motorista {name} já existe. Atualizando localização para o bairro {bairro_nome}.")
            check_name.lat = lat
            check_name.lon = lon
            check_name.bairro = bairro_nome
            connection.session.commit() 
            return check_name
        

        # Se o nome não existir, criar um novo registro
        new_driver = DriverQueue(name=name, telefone=telefone, bairro=bairro_nome, lat=lat, lon=lon)
    
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
    def tipo_bairro_embarque(cls, connection, bairro_embarque):
        ''' Verifica se o bairro está em nome_bairro ou  nome_alternativo '''
        
        bairro = connection.session.query(Bairros).filter(
            or_(
                Bairros.nome_bairro == bairro_embarque,
                Bairros.nome_alternativo == bairro_embarque
            )
        ).first()

        if bairro:
            return  bairro.tipo_bairro
                
        else: None
        

    @classmethod
    @db_connector
    def lat_lon_destino(cls, connection, bairro_destino):
        """Função para buscar latitude e longitude do bairro de destino no banco de dados"""
        
        # Verificar se o bairro existe no banco de dados
        bairro = connection.session.query(Bairros).filter(
            or_(
                Bairros.nome_bairro == bairro_destino,
                Bairros.nome_alternativo == bairro_destino
            )
        ).first()

        if bairro:
            # Retornar latitude e longitude do bairro encontrado
            return {
                'latitude': bairro.lat,
                'longitude': bairro.lon,
                'tipo_destino': bairro.tipo_bairro
            }
        
        else:
            print(f"Bairro {bairro_destino} não encontrado no banco de dados.")
            return None