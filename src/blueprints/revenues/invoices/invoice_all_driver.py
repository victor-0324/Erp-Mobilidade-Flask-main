# : disable= no-value-for-parameter
"""Retorna o fechamento de de todos os motoristas"""

import os
import tarfile
from flask import send_file

from src.blueprints.revenues.invoices.driver_invoice import DriverInvoice
from src.database.querys.drivers import MotoristsQuerys



class AllDriverInvoice():
    """Retorna o fechamento de todos os motoristas"""
    def __init__(self, daterange) -> None:
        """Realiza o fechamento de todos os motoristas"""
        self.daterange = daterange

        self.media_path = os.path.join(os.getcwd(), 'midia')
        self.tar_path = os.path.join(self.media_path, "fechamento.tar")

        # cria os arquivos
        self.get_invoices()


    def get_invoices(self):
        """Faz o fechamento de todos os motoristas e compacta em um arquivo"""
        for driver in self.get_drivers():
            DriverInvoice(self.daterange, driver).get_image()

        with tarfile.open(name=self.tar_path, mode="w:gz") as tar_file:
            for item in os.listdir(self.media_path):
                tar_file.add(os.path.join(self.media_path, item), arcname=f"{item}")


    def get_drivers(self):
        """Retorna os motoristas"""
        return list(map(lambda driver: driver.name, MotoristsQuerys.show())) # pylint: disable= no-value-for-parameter


    def send_image(self):
        """Envia o fechamento para download"""
        return send_file(
            self.tar_path,
            mimetype="application/x-tar",
            download_name=f"Fechamento {self.daterange}.tar",
        )


    def __enter__(self):
        """Inicia a classe"""
        return self
