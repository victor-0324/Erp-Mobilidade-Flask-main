"""Gerencia o envio de corridas"""



import requests

from ..querys import BotQuerys


class Corrida:
    """Processo de envio de corridas"""
    def __init__(self, embarque, bairro_embarque, bairro_destino, telefone) -> None:
        self.embarque = embarque
        self.bairro_embarque = bairro_embarque
        self.bairro_destino = bairro_destino
        self.telefone = telefone

    def endereco_em_geolocalizacao(self):

        api_token = 'pk.f17234d51a1015ab3c5ecb138de627c9'
        url = f'https://us1.locationiq.com/v1/search?key={api_token}&q={self.embarque}&format=json&'

        geolocalizacao = requests.get(
            url,
            timeout = 15
        )
        return geolocalizacao

    def motorista_mais_proximo(self):
        
        # verifica se tem um motorista no bairro que a pessoa pediu

        motorista = BotQuerys().motorista_da_vez(self.bairro_embarque)

        return motorista

    def definir_valor_da_corrida(self, bairro_embarque, bairro_destino):
        
        valor_da_corrida = None
        return valor_da_corrida
    
    def enviar_corrida(self, url):
        corrida = requests.post(
            url,
            params= {
                "bairro_embarque": self.bairro_embarque,
                "bairro_destino": self.bairro_destino,
                "telefone": self.telefone,
                "valor_da_corrida": self.valor_da_corrida
            },
            timeout = 15
        )

        return None



