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


class ClientQueue(Base):
    """Fila de Clientes"""

    __tablename__ = "client_queue"
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    telefone = Column(String(15))
    bairro = Column(String(255))
    date_time = Column(DateTime(), default=datetime.now)