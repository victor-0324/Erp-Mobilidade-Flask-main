# pylint: disable=too-few-public-methods, consider-using-f-string
"""User Querys"""

from sqlalchemy import or_
from sqlalchemy.orm.attributes import flag_modified
from src.database.db_connection import db_connector
from .models import Motoristas, Bairros
from .bairros import bairros
from datetime import datetime
import requests 
# key bot conversa
key = '26084536-20e3-4c12-98fc-dd6b30ba2417' 

class BotQuerys:
    """A Consult if name alredy exits"""
    @classmethod
    @db_connector
    def fila(cls, connection):
        """Return all motorists in database""" 

        return connection.session.query(Motoristas).all()



    @classmethod
    @db_connector
    def trocar_status_mot(cls, connection, tel_motorista):
        """Return all motorists in database""" 

        motorista = connection.session.query(Motoristas).filter_by(telefone=tel_motorista).first()
       
        motorista.status = 'livre'
        motorista.duracao_corrida=''
        motorista.inicio_corrida=None
        motorista.bairro_destino=''
        connection.session.commit()

        api_url = 'https://backend.botconversa.com.br/api/v1/webhooks-automation/catch/87780/zzNrLIRd0gUe/'

        params = {
            'Mot_telefone': tel_motorista 
        }

        headers = {
            'Authorization': f'API-KEY {key}',
            'Content-Type': 'application/json'
        }

        response = requests.post(api_url, json=params, headers=headers, timeout=30)

        if response.status_code == 200:
            print("Requisição enviada ao bot com sucesso!")
        else:
            print(f"Erro ao enviar requisição ao bot: {response.status_code}")
            print(response.text)
            
        return motorista
    
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
            motorista.bairro_destino = ''
            motorista.lat = lat
            motorista.lon = lon
            connection.session.commit()  
        else:
            lat = bairro.lat
            lon = bairro.lon 
            motorista.status = 'livre'
            motorista.duracao_corrida = ''
            motorista.inicio_corrida = None
            motorista.bairro_destino = ''
            motorista.bairro = bairro.nome_bairro
            motorista.lat = lat
            motorista.lon = lon
            connection.session.commit()  
            return 
   

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
            bairro_destino='', 
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
    def iniciar_corrida(cls, connection, telefone, bairro_destino,  duracao_total):
        """Iniciar uma corrida para o motorista"""
        
        motorista = connection.session.query(Motoristas).filter_by(telefone=telefone).first()
       
        if motorista and motorista.status == 'livre':
            agora = datetime.now()
            motorista.status = 'em_corrida'
            motorista.inicio_corrida = agora
            motorista.duracao_corrida = duracao_total 
            motorista.bairro_destino = bairro_destino
            connection.session.commit()
            print(f"motorista {motorista.name} iniciou uma corrida de duração {duracao_total}.")
        else:
            print(f"motorista {motorista.name} não está disponível para iniciar uma corrida.")


  
    @classmethod
    @db_connector
    def cancelar_corrida(cls, connection, mot_telefone):
        """Finalizar a corrida e marcar o DriverQueue como livre"""
        motorista = connection.session.query(Motoristas).filter_by(telefone=mot_telefone, status='em_corrida').first()

        if motorista:
            motorista.status = 'livre'
            motorista.inicio_corrida = None
            motorista.duracao_corrida = None
            connection.session.commit() 

            api_url = 'https://backend.botconversa.com.br/api/v1/webhooks-automation/catch/87780/zzNrLIRd0gUe/'
            key = '26084536-20e3-4c12-98fc-dd6b30ba2417'

            params = {
                'Mot_telefone': mot_telefone 
            }

            headers = {
                'Authorization': f'API-KEY {key}',
                'Content-Type': 'application/json'
            }

            response = requests.post(api_url, json=params, headers=headers, timeout=30)

            if response.status_code == 200:
                print("Requisição enviada cancelado!")
            else:
                print(f"Erro ao enviar requisição ao bot: {response.status_code}")
            
        else:
            print(f"O motorista {motorista.name} não está em uma corrida ativa para finalizar.")


    @classmethod
    @db_connector
    def desbloquear_mot(cls, connection, mot_telefone, cliente_telefone):
        ''' Remove o número do cliente da lista de clientes bloqueados do motorista '''

        # Busca o motorista pelo telefone
        motorista = connection.session.query(Motoristas).filter_by(telefone=mot_telefone).first()
        
        if motorista and motorista.cliente_bloqueado:
            # A lista de clientes bloqueados
            clientes_bloqueados = motorista.cliente_bloqueado

            if cliente_telefone in clientes_bloqueados:
                # Remove o cliente da lista
                clientes_bloqueados.remove(cliente_telefone)
                print(clientes_bloqueados)

                # Se a lista ficar vazia, define como None (NULL no banco)
                if not clientes_bloqueados:
                    motorista.cliente_bloqueado = None
                else:
                    # Caso contrário, atualiza com a lista modificada
                    motorista.cliente_bloqueado = clientes_bloqueados

                # Sinaliza ao SQLAlchemy que o campo foi modificado
                flag_modified(motorista, "cliente_bloqueado")

                # Confirma as alterações no banco de dados
                connection.session.commit()
                return {"status": "sucesso", "mensagem": "Cliente removido com sucesso."}

        return {"status": "erro", "mensagem": "Cliente não encontrado na lista ou motorista não encontrado."}


    @classmethod
    @db_connector
    def bloquear_motorista(cls, connection, mot_telefone, client_telefone):
        ''' Adiciona o número do cliente ao campo de cliente bloqueado do motorista ''' 

        # Busca o motorista pelo telefone
        motorista = connection.session.query(Motoristas).filter_by(telefone=mot_telefone).first()

        if not motorista:
            return {"status": "erro", "mensagem": "Motorista não encontrado."}

        # Inicializa a lista 'cliente_bloqueado' se não existir
        if motorista.cliente_bloqueado is None:
            motorista.cliente_bloqueado = [] 

        # Adiciona o cliente se não estiver na lista
        if client_telefone not in motorista.cliente_bloqueado:
            motorista.cliente_bloqueado.append(client_telefone)  
             # Imprima antes do commit para verificar a lista
            print(f"Clientes bloqueados antes do commit: {motorista.cliente_bloqueado}")

            # Informar ao SQLAlchemy que o campo foi modificado
            flag_modified(motorista, "cliente_bloqueado")
           
            connection.session.commit()

            return {"status": "sucesso", "mensagem": "Cliente bloqueado com sucesso."}
        
        return {"status": "erro", "mensagem": "Cliente já está bloqueado."}

    
    @classmethod
    @db_connector
    def remov_favorito(cls, connection, mot_telefone, cliente_telefone):
        ''' Adiciona o número do cliente ao campo de cliente favorito do motorista ''' 

         # Busca o motorista pelo telefone
        motorista = connection.session.query(Motoristas).filter_by(telefone=mot_telefone).first()
        
        if motorista and motorista.cliente_favorito:
            # A lista de clientes favoritos
            clientes_bloqueados = motorista.cliente_favorito

            if cliente_telefone in clientes_bloqueados:
                # Remove o cliente da lista
                clientes_bloqueados.remove(cliente_telefone)
                print(clientes_bloqueados)

                # Se a lista ficar vazia, define como None (NULL no banco)
                if not clientes_bloqueados:
                    motorista.cliente_favorito = None
                else:
                    # Caso contrário, atualiza com a lista modificada
                    motorista.cliente_favorito = clientes_bloqueados

                # Sinaliza ao SQLAlchemy que o campo foi modificado
                flag_modified(motorista, "cliente_favorito")

                connection.session.commit()
                return {"status": "sucesso", "mensagem": "Cliente removido com sucesso."}

        return {"status": "erro", "mensagem": "Cliente não encontrado na lista ou motorista não encontrado."}

    
    @classmethod
    @db_connector
    def adiciona_favorito(cls, connection, mot_telefone, client_telefone):
        ''' Adiciona o número do cliente ao campo de cliente favoritos do motorista ''' 

        # Busca o motorista pelo telefone
        motorista = connection.session.query(Motoristas).filter_by(telefone=mot_telefone).first()

        if not motorista:
            return {"status": "erro", "mensagem": "Motorista não encontrado."}

        # Inicializa a lista 'cliente_bloqueado' se não existir
        if motorista.cliente_favorito is None:
            motorista.cliente_favorito = [] 

        # Adiciona o cliente se não estiver na lista
        if client_telefone not in motorista.cliente_favorito:
            motorista.cliente_favorito.append(client_telefone)  

            # Informar ao SQLAlchemy que o campo foi modificado
            flag_modified(motorista, "cliente_favorito")
           
            connection.session.commit()
     
            return {"status": "sucesso", "mensagem": "Cliente bloqueado com sucesso."}
        
        return {"status": "erro", "mensagem": "Cliente já está bloqueado."}


    @classmethod
    @db_connector
    def adicionar_avaliacao(cls, connection, mot_telefone, nota):
        ''' Adiciona uma avaliação ao motorista e atualiza o total de avaliações e a nota total '''

        # Busca o motorista pelo telefone
        motorista = connection.session.query(Motoristas).filter_by(telefone=mot_telefone).first()

        if not motorista:
            return {"status": "erro", "mensagem": "Motorista não encontrado."}

        # Converte a nota de string para float
        nota = float(nota)

        # Inicializa as avaliações se não existirem
        if motorista.avalicoes == ' ':
            motorista.avalicoes = '0'  # Inicializa como string '0' se for None
        else:
            motorista.avalicoes = str(int(motorista.avalicoes))  # Converte para string

        # Converte o total de notas para float para a soma
        total_nota = float(motorista.total_nota) if motorista.total_nota else 0.0

        # Atualiza o total de avaliações e a nota total
        motorista.avalicoes = str(int(motorista.avalicoes) + 1)
        motorista.total_nota = str(total_nota + nota)

        # Salva as alterações no banco de dados
        connection.session.commit() 

        return {"status": "sucesso", "mensagem": "Avaliação adicionada com sucesso."} 


    @classmethod
    @db_connector
    def entrar_off(cls, connection, mot_telefone):
        """ Colocar o motorista em status 'off' """
        motorista = connection.session.query(Motoristas).filter_by(telefone=mot_telefone).first()
        print(motorista)
        if motorista:
            motorista.status = 'off'
            motorista.duracao_corrida = '' 
            motorista.bairro_destino = ''
            motorista.inicio_corrida = None
            motorista.hora_livre = None 
            connection.session.commit()
            print(f"DriverQueue {motorista.name} está agora offline.")
        else:
            print(f"DriverQueue {motorista.name} não encontrado.")

  
    @classmethod
    @db_connector
    def referecia(cls, connection, mot_telefone, referencia):
        ''' recebe a referencia do em barque do cliente ''' 

        motorista = connection.session.query(Motoristas).filter_by(telefone=mot_telefone).first() 

        if not motorista:
            return {"status": "erro", "mensagem": "Motorista não encontrado."} 
        
        
        api_url = "https://backend.botconversa.com.br/api/v1/webhooks-automation/catch/87780/WhywB8PVDDus/"


        params = {
                'referencia': referencia,
                'mot_telefone': mot_telefone
            }

        headers = {
            'Authorization': f'API-KEY {key}',
            'Content-Type': 'application/json'
        }

        response = requests.post(api_url, json=params, headers=headers, timeout=30)

        if response.status_code == 200:
            print("Requisição enviada ao bot com sucesso!")
        else:
            print(f"Erro ao enviar requisição ao bot: {response.status_code}")
            print(response.text)
            
        return motorista
