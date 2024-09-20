# pylint: disable = consider-using-f-string
from typing import List

from sqlalchemy import text, inspect

from src.database.db_connection import db_connector
from src.database.models import runs_factory


class RunsQuerys:
    """A Consult if name alredy exits"""

    @classmethod
    @db_connector
    def create_table(cls, connection, name):
        """Create runs table."""

        driver = runs_factory(name)
        engine = connection.get_engine()
        inspector = inspect(engine)

        # Verificar se a tabela já existe
        if not inspector.has_table(driver.__tablename__):
            # Se a tabela não existir, criar todas as tabelas (incluindo a desejada)
            driver.metadata.create_all(engine)

    @classmethod
    @db_connector
    def insert(cls, connection, name, data):
        table_name = f"runs_{name.lower()}"
        statement = text(
            f"INSERT IGNORE INTO {table_name} (date_time, valor, operation) "
            "VALUES (:date_time, :valor, :operation)"
        )
        for item in data:
            connection.session.execute(
                statement,
                {"date_time": item[0], "valor": item[1], "operation": item[2]},
            )
        connection.session.commit()


    @classmethod
    @db_connector
    def search_daterange(cls, connection, name: str, date_range: List) -> List:
        """Procura as corrida de um determinado motorista em um 
        intervalo de duas datas.

        name -- driver name
        date_range -- is a list with two datetimes.

        For exemple:
                '2021-01-15 07:42:00', '2021-01-20 16:20:00'

        Return a list with all runs
        """

        mot = runs_factory(name)
        runs = (
            connection.session.query(mot)
            .filter(mot.date_time.between(*date_range))
            .all()
        )

        _runs = list(
            map(
                lambda run: (
                    # run.date_time,
                    run.valor,
                    run.operation,
                ),
                runs,
            )
        )
        return _runs
