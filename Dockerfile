# Utilize uma imagem base oficial de Python
FROM python:3.12

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos do projeto para o diretório de trabalho
COPY . /app

# Configurar o locale para Português do Brasil
RUN apt-get update && apt-get install -y locales && \
    sed -i -e 's/# pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen

ENV LANG pt_BR.UTF-8
ENV LANGUAGE pt_BR:pt
ENV LC_ALL pt_BR.UTF-8


# Instale as dependências do projeto
RUN pip install -r requirements.txt

# Exponha a porta em que sua aplicação irá rodar
EXPOSE 8000

# Comando para executar a aplicação
# CMD ["python", "wsgi.py"]

CMD ["gunicorn", "-b", "0.0.0.0:5002", "wsgi:app"]