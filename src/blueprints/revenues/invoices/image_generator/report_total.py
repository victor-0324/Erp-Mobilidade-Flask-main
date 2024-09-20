"""Gerador de imagem"""
from datetime import datetime
import locale
import os
from PIL import Image, ImageDraw, ImageFont
locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")


class CompanyImageGenerator:
    """Gerador de imagem"""

    def __init__(self, data) -> None:
        """Iniciando Gerador de imagem"""
        self.drivers = data["drivers"]
        self.drivers_amount = len(self.drivers)
        
        self.runs_amount = data["runs_amount"]
        self.gross_value = data["gross_value"]
        self.profit = data["profit"]

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
        self.height = 330 + (self.drivers_amount * 20)

        # medida da tabela
        self.table_height = 290

        with Image.new(
            "RGBA", (self.width, self.height), color="#E5E5E5") as self.image:
            self.draw_header()
            self.draw_infos()
            self.draw_faturations()
            self.draw_table()
            # self.draw_image()

        self.image.save(os.path.join(os.getcwd(), "midia", "total.png"), "PNG")


    def draw_header(self):
        """Desenhando cabecalho"""
        top_retangle = ImageDraw.Draw(self.image)
        top_retangle.rectangle([(0, 0), (595, 86)], fill="#1A336B")
        top_retangle.text(
            (40, 27),
            "Fatura Semanal - G4 Mobile",
            (255, 255, 255),
            font=ImageFont.truetype(self.font_path, 24),
        )
        
        logo = Image.open(self.logo_path)
        self.image.alpha_composite(logo, (370, 16))
        
    def draw_infos(self):
        """Desenhando data inicial, final, numero de motoristas"""
        content_retangle = ImageDraw.Draw(self.image)
        # content_retangle.rectangle([(596, 86), (595, 86)], fill="#E5E5E5")

        content_retangle.text(
            (40, 110), "Data Inicial:", (0, 0, 0), font=ImageFont.truetype(self.font_path, 14)
        )
        
        data_retangle = ImageDraw.Draw(self.image)
        data_retangle.rectangle(
            [(40, 130), (180, 160)], fill="#E5E5E5", outline="#000000"
        )
        
        data_retangle.text(
            (45, 135),
            f"{self.date_one}",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 18),
        )
        
        content_retangle.text(
            (200, 110), "Data Final:", (0, 0, 0), font=ImageFont.truetype(self.font_path, 14)
        )
        date_two_retangle = ImageDraw.Draw(self.image)
        date_two_retangle.rectangle(
            [(200, 130), (340, 160)], fill="#E5E5E5", outline="#000000"
        )
        
        date_two_retangle.text(
            (205, 135),
            f"{self.date_two}",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 18),
        )
        
        content_retangle.text(
            (360, 110), "Nº de Motoristas:", (0, 0, 0), font=ImageFont.truetype(self.font_path, 14)
        )
        amount_retangle = ImageDraw.Draw(self.image)
        amount_retangle.rectangle(
            [(360, 130), (500, 160)], fill="#E5E5E5", outline="#000000"
        )
        
        date_two_retangle.text(
            (370, 135),
            f"{self.drivers_amount}",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 18),
        )
        

    def draw_faturations(self):
        """Desenhando faturamento"""
        content_retangle = ImageDraw.Draw(self.image)
        # content_retangle.rectangle([(596, 86), (595, 86)], fill="#E5E5E5")

        content_retangle.text(
            (40, 180), "Nº de Corridas:", (0, 0, 0), font=ImageFont.truetype(self.font_path, 14)
        )

        runs_retangle = ImageDraw.Draw(self.image)
        runs_retangle.rectangle(
            [(40, 200), (180, 230)], fill="#E5E5E5", outline="#000000"
        )

        runs_retangle.text(
            (45, 205),
            f"{self.runs_amount}",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 18),
        )

        content_retangle.text(
            (200, 180), "Valor Bruto:", (0, 0, 0), font=ImageFont.truetype(self.font_path, 14)
        )
        date_two_retangle = ImageDraw.Draw(self.image)
        date_two_retangle.rectangle(
            [(200, 200), (340, 230)], fill="#E5E5E5", outline="#000000"
        )

        content_retangle.text(
            (205, 205),
            f"{locale.currency(self.gross_value)}",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 18),
        )

        content_retangle.text(
            (360, 180), "Lucro Total:", (0, 0, 0), font=ImageFont.truetype(self.font_path, 14)
        )
        amount_retangle = ImageDraw.Draw(self.image)
        amount_retangle.rectangle(
            [(360, 200), (500, 230)], fill="#E5E5E5", outline="#000000"
        )

        content_retangle.text(
            (365, 205),
            f"{locale.currency(self.profit)}",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 18),
        )
        
        

    def draw_table(self):
        """Desenhando imagem"""
        content_retangle = ImageDraw.Draw(self.image)


        
        table_retangle = ImageDraw.Draw(self.image)
        table_retangle.rectangle(
            [(40, 250), (550, (self.table_height + (self.drivers_amount * 20)))], fill="#E5E5E5", outline="#000000"
        )
        content_retangle.text(
            (85, 260), "Nome:", (0, 0, 0), font=ImageFont.truetype(self.font_path, 14)
        )

        content_retangle.text(
            (230, 260),
            "Quant.:",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 14),
        )

        content_retangle.text(
            (320, 260),
            "Recebeu:",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 14),
        )

        content_retangle.text(
            (420, 260),
            "A Pagar:",
            (0, 0, 0),
            font=ImageFont.truetype(self.font_path, 14),
        )

        valor = 285

        for driver in self.drivers:
            
            content_retangle.text(
                (50, valor),
                driver["name"],
                (0, 0, 0),
                font=ImageFont.truetype(self.font_path, 11),
            )

            content_retangle.text(
                (245, valor),
                f"{driver['runs_amount']}",
                (0, 0, 0),
                font=ImageFont.truetype(self.font_path, 11),
            )
            
            content_retangle.text(
                (340, valor),
                f"{locale.currency(driver['total_receved'])}",
                (0, 0, 0),
                font=ImageFont.truetype(self.font_path, 11),
            )
            
            content_retangle.text(
                (435, valor),
                f"{locale.currency(driver['total_to_pay'])}",
                (0, 0, 0),
                font=ImageFont.truetype(self.font_path, 11),
            )
            
            
            

            # content_retangle.text(
            #     (200, valor),
            #     f"{driver}",
            #     (0, 0, 0),
            #     font=ImageFont.truetype(self.font_path, 12),
            # )

            # content_retangle.text(
            #     (300, valor),
            #     f"{locale.currency(row[2])}",
            #     (0, 0, 0),
            #     font=ImageFont.truetype(self.font_path, 12),
            # )

            # content_retangle.text(
            #     (420, valor),
            #     f"{locale.currency(row[3])}",
            #     (0, 0, 0),
            #     font=ImageFont.truetype(self.font_path, 12),
            # )
            valor = valor + 20

        

        self.image.convert("RGB")
        
        
    def insert_driver(self):
        """Inserindo dados dos motorista"""
        pass