"""Arquivo com configuração das regras"""

import json
from typing import NamedTuple, List, Tuple, Dict

from src.database.querys.rules import RulesQuery
from src.database.querys.drivers import MotoristsQuerys
class RuleData(NamedTuple):
    """Regras"""
    tag: str
    rule_type: List[str]
    shield: str
    condition: str
    condition_value: int
    rule: str
    rule_value: int

class DriverRulesData(NamedTuple):
    """Motorista"""
    name: str
    tag: str
    revenue: int
    porcents: Dict
    invoice: int


class SetRules:
    """Processamento baseado em condições"""
    def __init__(self, driver, total_recived):
        """Montando regras"""
        self.rules = RulesQuery().get_all()
        
        self.driver = MotoristsQuerys().check_name(driver)
        self.total_receved = total_recived


    def get_porcent(self):
        """Verifica quais regras devem ser usadas a partir da tag do motorista"""
        verifyed_rules = []
        for rule in self.rules:
            data_json: dict = rule.data_json
            driver_tag = self.driver.data_json.get("tag")
            if not driver_tag:
                driver_tag = "Padrão"
            if data_json.get("tag") == driver_tag:
                if self.check_condition(data_json) is not False:
                    verifyed_rules.append(data_json)
        
        print(verifyed_rules)

        if len(verifyed_rules) > 1:
            result = max(verifyed_rules, key=lambda x: x.get("condition_value"))
        else:
            result = verifyed_rules[0]

        return result.get("rule_value")

    
    def check_sheld(self):
        """Verifica o campo a ser consultado"""
        match self.driver.shield:
            case "Fat. do Motorista":
                return self.driver.revenue

    def check_condition(self, rule):
        """Verifica qual o critério de comparação"""
        total = self.total_receved
        condition = rule.get("condition")
        condition_value = int(rule.get("condition_value"))
        porcent = int(rule.get("rule_value"))

        print(total, condition, condition_value, porcent)
        
        if condition == "Menor que":
            if self.total_receved < condition_value:
                return porcent
        elif condition == "Maior que":
            if self.total_receved > condition_value:
                return porcent
            
        print("erro na condição")
        return False



