# pylint: disable=no-value-for-parameter
"""Receave mmotorist runs"""

import datetime
import re
from traceback import print_tb

from werkzeug.datastructures import FileStorage

from src.database.querys import MotoristsQuerys, RunsQuerys


class MotoristsDataParsing:
    """Parse informations of files and create sql tables."""

    def __init__(self, request_files) -> None:
        """Receve files to parse
        This files are a .txt files"""

        self.request_files = request_files
        self.set_motorists()


    def set_motorists(self):
        """Set name for the driver"""
        for driver in self.request_files:
            data = ParsedMotoristData(driver).get()
            name = driver.filename[:-4][29:].replace(" ", "_")
            data_json = {"tag": "Padrão"}
            MotoristsQuerys.new(name, data_json)
            RunsQuerys.create_table(name)
            RunsQuerys.insert(name, data)


class ParsedMotoristData:
    """Percore toda a conversa pegando apenas
    as linhas correspondentes aos codigos usados em
    nossa regra de negocio
    """

    def __init__(self, talk: FileStorage):
        """Recebe uma conversa"""
        self.data_frame = []
        self.filter_talk(talk, "G4 MOBILE", "reais")

    def get(self):
        """Metodo para acessar o dataframe"""
        return self.data_frame

    def get_datetime(self, line: str) -> str:
        """Realiza o parsing da data"""
        date = re.findall(r"\d+/\d+/\d+", line)

        if not date:
            pass

        date = datetime.datetime.strptime(date[0], "%d/%m/%Y").strftime("%Y-%m-%d")
        hour = re.findall(r"\d+\:\d+", line)
        hour = hour[0] + ":00"
        date_time = f"{date} {hour}"
        try:
            if date_time == self.data_frame[-1][0]:
                correction = str(int(date_time[14:-3]) + 1)
                date_time_list = list(date_time)
                date_time_list[14] = correction[0]
                date_time_list[15] = correction[1]
                date_time = "".join(date_time_list)
        except Exception as error:
            print(error)
        return date_time

    def get_valor(self, line: str) -> str:
        """Realiza o parsing do valor"""
        return re.findall(r"\d+\s+reais", line)[0][:-6]

    def get_operation(self, line: str) -> str:
        """Realiza o parsing do valor"""
        if "desconto no boleto" in line:
            return "-"
        else:
            return "+"

    def filter_talk(self, talk, name, rule):
        """Percorre toda a conversa: talk
        procurando por
            Refatora as Linhas no formato
            datetime | valor | operation
        """
        count = 0

        for line in talk:
            line = line.decode("utf-8")
            if name in line:
                if rule in line:
                    count += 1
                    # print(type(line))
                    try:
                        format_line = [
                            self.get_datetime(line),
                            self.get_valor(line),
                            self.get_operation(line),
                        ]
                        self.data_frame.append(format_line)
                    except Exception as error:
                        print(error, line)
