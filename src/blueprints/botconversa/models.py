"""Fila de Motoristas"""



from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

from src.database import Base


class DriverQueue(Base):
    """Fila de Motoristas"""

    __tablename__ = "driver_queue"
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    telefone = Column(String(15))
    lat = Column(String(150))
    lon = Column(String(150))
    bairro = Column(String(255))
    date_time = Column(DateTime(), default=datetime.now)


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


