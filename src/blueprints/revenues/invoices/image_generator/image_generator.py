"""Gerador de imagem"""
from datetime import datetime
import locale
import os
from PIL import Image, ImageDraw, ImageFont
locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")


class ImageGenerator:
    """Gerador de imagem"""

    def __init__(self, data, motorist_id="000") -> None:
        """Iniciando Gerador de imagem"""
        self.name = data["name"]
        self.motorist_id = motorist_id
        self.runs_amount = data["runs_amount"]
        self.total_receved = data["total_receved"]
        self.total_to_pay = data["total_to_pay"]
        self.dataframe = data["dataframe"]

        self.date_one = datetime.strftime(
            datetime.strptime(
                data["daterange"][0], "%Y-%m-%d %H:%M:%S"
                ), "%d/%m/%Y"
            )

        self.date_two = datetime.strftime(
            datetime.strptime(
                data["daterange"][1], "%Y-%m-%d %H:%M:%S"
                ), "%d/%m/%Y"
            )

        # Caminhos para as fontes
        self.font_path = "./src/static/dist/fonts/Roboto-Regular.ttf"

        # Caminhos para a logo
        self.logo_path = "./src/static/dist/img/logo.png"

        # Medidas da imagem
        self.width = 595
        self.height = 842

        with Image.new(
            "RGBA", (self.width, self.height), color="#E5E5E5"
        ) as self.image:
            self.draw_image()

        self.image.save(os.path.join(os.getcwd(), "midia", self.name.lower()+".png"), "PNG")


    def draw_image(self):
        """Desenhando imagem"""

        # Top Retangle
        top_retangle = ImageDraw.Draw(self.image)
        top_retangle.rectangle([(0, 0), (595, 86)], fill="#1A336B")
        top_retangle.text(
            (40, 27),
            "Fatura Semanal - G4 Mobile",
            (255, 255, 255),
            font=ImageFont.truetype(self.font_path, 24),
        )

        # Content Retangle
        content_retangle = ImageDraw.Draw(self.image)
        # content_retangle.rectangle([(596, 86), (595, 86)], fill="#E5E5E5")

        table_retangle = ImageDraw.Draw(self.image)
        table_retangle.rectangle(
            [(40, 260), (550, 630)], fill="#E5E5E5", outline="#000000"
        )

        content_retangle.text(
            (40, 110), "Nome:", (0, 0, 0), font=ImageFont.truetype(self.font_path, 14)
        )
        name_retangle = ImageDraw.Draw(self.image)
        name_retangle.rectangle(
            [(40, 130), (550, 160)], fill="#E5E5E5", outline="#000000"
        )

        content_retangle.text(
            (40, 180), "ID:", (0, 0, 0), font=ImageFont.truetype(self.font_path, 14)
        )
        id_retangle = ImageDraw.Draw(self.image)
        id_retangle.rectangle(
            [(40, 200), (180, 230)], fill="#E5E5E5", outline="#000000"
        )

        content_retangle.text(
            (250, 180),
            "Data Inicial:",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 14),
        )

        data_one_retangle = ImageDraw.Draw(self.image)
        data_one_retangle.rectangle(
            [(250, 200), (380, 230)], fill="#E5E5E5", outline="#000000"
        )

        content_retangle.text(
            (420, 180),
            "Data Final:",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 14),
        )

        data_two_retangle = ImageDraw.Draw(self.image)
        data_two_retangle.rectangle(
            [(420, 200), (550, 230)], fill="#E5E5E5", outline="#000000"
        )

        content_retangle.text(
            (85, 270), "Valor:", (0, 0, 0), font=ImageFont.truetype(self.font_path, 14)
        )

        content_retangle.text(
            (180, 270),
            "Quantidade:",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 14),
        )

        content_retangle.text(
            (300, 270),
            "Recebido:",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 14),
        )

        content_retangle.text(
            (420, 270),
            "A Pagar:",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 14),
        )

        content_retangle.text(
            (50, 660),
            "Total de Corridas",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 14),
        )

        total_runs_retangle = ImageDraw.Draw(self.image)
        total_runs_retangle.rectangle(
            [(48, 680), (189, 720)], fill="#E5E5E5", outline="#000000"
        )

        content_retangle.text(
            (232, 660),
            "Total Recebido",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 14),
        )

        total_recived_retangle = ImageDraw.Draw(self.image)
        total_recived_retangle.rectangle(
            [(230, 680), (370, 720)], fill="#E5E5E5", outline="#000000"
        )

        content_retangle.text(
            (400, 660),
            "Total a Pagar",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 14),
        )

        total_to_pay_retangle = ImageDraw.Draw(self.image)
        total_to_pay_retangle.rectangle(
            [(400, 680), (530, 720)], fill="#E5E5E5", outline="#000000"
        )

        # Footer Retangle
        footer_retangle = ImageDraw.Draw(self.image)
        footer_retangle.rectangle([(0, 742), (595, 842)], fill="#1A336B")

        content_retangle.text(
            (150, 755),
            "Muito Obrigado pela sua Colaboração! \n"
            "A Forma de Pagamento estará no Grupo da Diretória \n"
            "",
            (255, 255, 255),
            font=ImageFont.truetype(self.font_path, 15),
            align="center",
        )

        valor = 290


        content_retangle.text(
            (95, 689),
            f"{self.runs_amount}",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 20),
        )

        content_retangle.text(
            (245, 689),
            f"{locale.currency(self.total_receved)}",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 18),
        )

        content_retangle.text(
            (415, 689),
            f"{locale.currency(self.total_to_pay)}",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 18),
        )

        content_retangle.text(
            (55, 137),
            "{}".format(self.name),
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 18),
        )

        content_retangle.text(
            (55, 205),
            "{}".format(self.motorist_id),
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 18),
        )

        content_retangle.text(
            (260, 205),
            f"{self.date_one}",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 18),
        )

        content_retangle.text(
            (430, 205),
            f"{self.date_two}",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 18),
        )

        for row in self.dataframe:
            
            content_retangle.text(
                (80, valor),
                f"{locale.currency(row[0])}",
                (0, 0, 0),
                font=ImageFont.truetype(self.font_path, 12),
            )

            content_retangle.text(
                (200, valor),
                f"{row[2]}",
                (0, 0, 0),
                font=ImageFont.truetype(self.font_path, 12),
            )

            content_retangle.text(
                (300, valor),
                f"{locale.currency(row[3])}",
                (0, 0, 0),
                font=ImageFont.truetype(self.font_path, 12),
            )

            content_retangle.text(
                (420, valor),
                f"{locale.currency(row[4])}",
                (0, 0, 0),
                font=ImageFont.truetype(self.font_path, 12),
            )
            valor = valor + 20
        logo = Image.open(self.logo_path)
        self.image.alpha_composite(logo, (370, 16))
        self.image.convert("RGB")

        return True
