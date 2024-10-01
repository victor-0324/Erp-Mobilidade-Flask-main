"""Fila de Motoristas"""



from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON

from src.database import Base


class Motoristas(Base):
    """ Fila de Motoristas """

    __tablename__ = "motoristas"
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    telefone = Column(String(20))
    sexo = Column(String(50))
    tipo_carro = Column(String(20))
    total_nota = Column(String(20))  
    avalicoes = Column(String(20))
    lat = Column(String(150))
    lon = Column(String(150))
    bairro = Column(String(255))
    status = Column(String(50))                     # Status do motorista: livre, em_corrida.
    hora_livre = Column(DateTime)                   # Momento em que o motorista ficou livre
    inicio_corrida = Column(DateTime)               # Hora em que a corrida começou
    duracao_corrida = Column(String(100))           # Duração da corrida (recebida da API)
    tempo_restante_corrida = Column(String(100))    # Tempo restante da corrida
    cliente_bloqueado = Column(JSON)  
    cliente_favorito = Column(JSON) 
    
class Endereco(Base):
    """ Endereços clientes """

    __tablename__ = "enderecos"
    id = Column(Integer, primary_key=True)
    rua = Column(String(120))
    numero = Column(String(20))
    bairro = Column(String(255))
    

class Bairros(Base):
    """ Bairros """

    __tablename__ = "bairros"
    id = Column(Integer, primary_key=True)
    nome_bairro = Column(String(120))
    tipo_bairro = Column(String(100))
    nome_alternativo = Column(String(255))
    lat = Column(String(150))
    lon = Column(String(150)) 
    cidade = Column(String(150))
    cep = Column(String(50))


