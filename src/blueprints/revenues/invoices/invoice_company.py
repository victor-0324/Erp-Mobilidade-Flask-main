# pylint: disable= no-value-for-parameter
"""Retorna o fechamento da empresa"""

import os
from flask import send_file

from src.blueprints.revenues.invoices.driver_invoice import DriverInvoice
from src.blueprints.revenues.invoices.image_generator.report_total import CompanyImageGenerator

from src.database.querys.drivers import MotoristsQuerys


class CompanyInvoice():
    """Retorna o fechamento da empresa"""

    def __init__(self, daterange) -> None:
        """Realiza o fechamento da empresa"""
        self.daterange = daterange
        self.drivers = []

        self.runs_amount = 0
        self.gross_value = 0
        self.profit = 0

        self.set_data()


    def set_data(self):
        """Faz o fechamento de todos os motoristas e compacta em um arquivo"""
        for driver in self.get_drivers():
            _driver = DriverInvoice(self.daterange, driver).get_result()

            # Soma ao resultado Total
            self.runs_amount += _driver["runs_amount"]
            self.gross_value += _driver["total_receved"]
            self.profit += _driver["total_to_pay"]

            # Adciona o motorista na lista
            self.drivers.append(_driver)


    def get_drivers(self):
        """Retorna os motoristas"""
        return list(map(lambda driver: driver.name, MotoristsQuerys.show())) # pylint: disable= no-value-for-parameter


    def get_image(self):
        """Retorna a imagem do fechamento"""
        CompanyImageGenerator(self.get_result())
        return send_file(
            os.path.join(os.getcwd(), "midia", "total.png"),
            mimetype="png",
            download_name="total.png",
            as_attachment=True
        )


    def get_result(self):
        """Retorna o resultado"""
        return {
            "daterange": self.daterange,
            "drivers": self.drivers,
            "runs_amount": self.runs_amount,
            "gross_value": self.gross_value,
            "profit": round(self.profit, 2)
        }
