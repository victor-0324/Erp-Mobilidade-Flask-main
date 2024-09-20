"""Retorna o fechamento de um inico motorista"""

from collections import Counter
from typing import Tuple
from src.blueprints.revenues.invoices.image_generator.image_generator import ImageGenerator

from src.database.querys.runs import RunsQuerys
from src.database.querys.drivers import MotoristsQuerys

from .rules import SetRules

# class Porcents(NamedTuples):
    
    

class DriverInvoice:
    """Retorna o fechamento de um unico motorista"""

    def __init__(self, daterange, name) -> None:
        """Realiza o fechamento do motorista"""
        self.name = name
        self.daterange = daterange

        # Coleta os dados em um intervalo de tempo
        self.runs = Counter(self.get_driver_data(name, daterange))

        # analisa o faturamento e calcula o resultado
        self.incidences: list = self.set_incidences()

        self.runs_amount = self.calc_runs_amount()
        self.total_receved = self.set_total_receved()
        
        self.porcent = SetRules(name, self.total_receved).get_porcent()
        self.porcent = int(self.porcent) / 100
        
        self.total_to_pay = self.set_total_to_pay()
        



    def get_driver_data(self, name, daterange) -> None:
        """Coleta os dados do fechamento dos motoristas."""
        return RunsQuerys.search_daterange(name, daterange) #pylint: disable= no-value-for-parameter

    def set_incidences(self):
        """Define as incidencias"""
        return [
            self.calc_values(item, self.runs[item])
            for item in self.runs
        ]

    def calc_values(self, item: Tuple, amount: int):
        """Define os porcentuais
        item = (valor:int, tipo:str, quantidade:int)
        item_after = (item*, total_recebido:int)
        """
        total = item[0] * amount

        result = item + (amount, total)

        return result


    def calc_runs_amount(self) -> int:
        """Define o valor total de corridas"""            
        return sum(item[2] for item in self.incidences)


    def set_total_receved(self) -> int:
        """Define o valor total recebido"""
        total = sum(item[3] for item in self.incidences)
        return total


    def set_total_to_pay(self) -> int:
        """Define o valor total a pagar"""
        
        self.incidences = [
            self.set_porcents(item)
            for item in self.incidences
        ]
        
        soma = sum(item[4] for item in self.incidences)
            
        if soma <= 50:
            return 50

        return soma

    def set_porcents(self, item):
        """Define os porcentuais"""
        
        if item[1] == '+':
            porcent = self.porcent # 0.10
            result = item[3] * porcent


        if item[1] == '-':
            porcent = -1.0 * self.porcent
            result = (item[3] + (item[3] * porcent) )* -1
            

        return item + (result,)

    def get_group_by_name(self):
        """Pick group by name"""
        defaut_group = MotoristsQuerys.get_group(self.name) # pylint: disable= no-value-for-parameter

        if defaut_group == "Padrão":
            if self.total_receved <= 1400:
                return defaut_group
            elif self.total_receved >= 1400 and self.total_receved <= 1800:
                return '1400+'
            elif self.total_receved >= 1800 and self.total_receved <= 2200:
                return '1800+'
            elif self.total_receved >= 2200:
                return '2200+'
        return defaut_group


    def get_result(self):
        """Retorna o resultado final"""
        return {
            "name": self.name,
            "daterange": self.daterange,
            "group": "Padrão",
            "runs_amount": self.runs_amount,
            "dataframe": self.incidences,
            "total_receved": round(self.total_receved, 2),
            "total_to_pay": round(self.total_to_pay, 2)
        }


    def get_image(self):
        """Retorna a imagem"""
        ImageGenerator(data=self.get_result())
