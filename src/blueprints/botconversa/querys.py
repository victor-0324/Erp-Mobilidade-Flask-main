# pylint: disable=too-few-public-methods, consider-using-f-string
"""User Querys"""

from sqlalchemy import or_
from src.database.db_connection import db_connector
from .models import Motoristas, Bairros
from .bairros import bairros
from datetime import datetime

class BotQuerys:
    """A Consult if name alredy exits"""
    @classmethod
    @db_connector
    def fila(cls, connection):
        """Return all motorists in database"""
        return connection.session.query(Motoristas).all()

    @classmethod
    @db_connector
    def buscar_motorista_por_tel(cls, connection, tel_motorista):
        """Return all motorists in database"""
        motorista = connection.session.query(Motoristas).filter_by(telefone=tel_motorista).first()
        return motorista
    

    @classmethod
    @db_connector
    def atualizar_status_motorista(cls, connection, motorista_troca):
        ''' Atualiza o status do motorista a pos o pedido de troca do cliente ''' 

        motorista_troca.status = 'livre'
        motorista_troca.duracao_corrida='', 
        connection.session.commit()


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
    def cadastrar_motorista(cls, connection, name, sexo, telefone, tipo_carro):
        ''' Cadastrar um motorista '''

         # Criar uma nova instância da classe Motoristas
        novo_motorista = Motoristas(
            name=name,
            sexo=sexo,
            telefone=telefone,
            tipo_carro=tipo_carro,
            total_nota='0',  
            avalicoes='0',  
            lat='0',
            lon='0', 
            bairro='',  
            status='off',
            hora_livre=None,
            inicio_corrida=None, 
            duracao_corrida='', 
            tempo_restante_corrida='', 
            cliente_bloqueado=None,
            cliente_favorito=None
        )

        # Adicionar o novo motorista à sessão do banco de dados
        connection.session.add(novo_motorista)
        
        # Confirmar a transação (salvar no banco de dados)
        connection.session.commit()

        return novo_motorista


    @classmethod
    @db_connector
    def livre(cls, connection, telefone, bairro):
        """Função para adicionar novo motorista ou atualizar localização"""
      
        motorista = connection.session.query(Motoristas).filter_by(telefone=telefone).first()
        bairro = connection.session.query(Bairros).filter_by(nome_bairro=bairro).first()
    
        if bairro and motorista.status == 'off' or motorista.status == 'em_corrida':
            lat = bairro.lat
            lon = bairro.lon 
            motorista.status = 'livre'
            agora = datetime.now()
            motorista.bairro = bairro.nome_bairro
            motorista.hora_livre = agora
            motorista.duracao_corrida = ''
            motorista.inicio_corrida = None
            motorista.lat = lat
            motorista.lon = lon
            connection.session.commit()  
        else:
            lat = bairro.lat
            lon = bairro.lon 
            motorista.status = 'livre'
            motorista.duracao_corrida = ''
            motorista.inicio_corrida = None
            motorista.bairro = bairro.nome_bairro
            motorista.lat = lat
            motorista.lon = lon
            connection.session.commit()  
            return 
   
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
        

    @classmethod
    @db_connector
    def iniciar_corrida(cls, connection, telefone, duracao_total):
        """Iniciar uma corrida para o motorista"""
        
        motorista = connection.session.query(Motoristas).filter_by(telefone=telefone).first()

        if motorista and motorista.status == 'livre':
            agora = datetime.now()
            motorista.status = 'em_corrida'
            motorista.inicio_corrida = agora
            motorista.duracao_corrida = duracao_total
            connection.session.commit()
            print(f"motorista {motorista.name} iniciou uma corrida de duração {duracao_total}.")
        else:
            print(f"motorista {motorista.name} não está disponível para iniciar uma corrida.")


    @classmethod
    @db_connector
    def calcular_tempo_restante_corrida(cls, connection, name):
        """Calcular o tempo restante da corrida"""
        DriverQueue = connection.session.query(Motoristas).filter_by(name=name, status='em_corrida').first()

        if DriverQueue and DriverQueue.inicio_corrida:
            agora = datetime.now()
            tempo_decorrido = agora - DriverQueue.inicio_corrida
            tempo_restante = DriverQueue.duracao_esperada_corrida - tempo_decorrido

            print(f"Tempo restante da corrida para {name}: {tempo_restante}")
            return tempo_restante
        else:
            print(f"DriverQueue {name} não está em uma corrida.")
            return None

    @classmethod
    @db_connector
    def finalizar_corrida(cls, connection, name):
        """Finalizar a corrida e marcar o DriverQueue como livre"""
        DriverQueue = connection.session.query(Motoristas).filter_by(name=name, status='em_corrida').first()

        if DriverQueue:
            DriverQueue.status = 'livre'
            DriverQueue.inicio_corrida = None
            DriverQueue.duracao_esperada_corrida = None
            connection.session.commit()
            print(f"DriverQueue {name} finalizou a corrida e está agora livre.")
        else:
            print(f"DriverQueue {name} não está em uma corrida ativa para finalizar.")

    @classmethod
    @db_connector
    def entrar_off(cls, connection, name):
        """Colocar o DriverQueue em status 'off'"""
        DriverQueue = connection.session.query(Motoristas).filter_by(name=name).first()

        if DriverQueue:
            DriverQueue.status = 'off'
            DriverQueue.inicio_corrida = None
            DriverQueue.duracao_esperada_corrida = None
            connection.session.commit()
            print(f"DriverQueue {name} está agora offline.")
        else:
            print(f"DriverQueue {name} não encontrado.")

    @classmethod
    @db_connector
    def voltar_trabalho(cls, connection, name):
        """Colocar o DriverQueue de volta ao status 'livre' após estar 'off'"""
        DriverQueue = connection.session.query(Motoristas).filter_by(name=name, status='off').first()

        if DriverQueue:
            DriverQueue.status = 'livre'
            connection.session.commit()
            print(f"DriverQueue {name} voltou ao trabalho e está agora livre.")
        else:
            print(f"DriverQueue {name} não estava offline ou não foi encontrado.")