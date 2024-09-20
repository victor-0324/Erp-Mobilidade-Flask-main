# pylint: disable=too-few-public-methods
"""Configurações para o projeto
Para passar determinadas variaveis e constantes para o sistemas
esteremos utilizando objetos com diferentes propriedades para
cada ambiente. Para setar esse ambiente va para
"""

import getpass
import os
from os.path import join

from dotenv import load_dotenv


class Config:
    """Configurações globais para todo o projeto"""

    user_dir = "D:\Erp-Mobilidade-Flask\.env"
    load_dotenv(user_dir)

    SECRET_KEY = os.environ.get("SECRET_KEY")
    UPLOAD_FOLDER = os.environ.get("MIDIA_PATH")
    MIDIA_PATH = join(os.getcwd(), "midia")
    ALLOWED_EXTENSIONS = {
        "txt",
    }
    # DATABASE_CONNECTION = os.environ.get("DATABASE_CONNECTION")
    DATABASE_CONNECTION = "mariadb+pymysql://root:159753@127.0.0.1:3306/mobilidade"

class TestingConfig(Config):
    """Ambiente de testes"""

    DEBUG = False
    TESTING = True


class ProductionConfig(Config):
    """Ambiente de produção"""

    DEBUG = False
