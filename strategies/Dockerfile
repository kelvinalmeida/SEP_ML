# Usar a imagem oficial do Python
FROM python:3.9

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar os arquivos do projeto para o container
COPY . .

# Instalar as dependências
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Definir a variável de ambiente para ativar o modo de desenvolvimento do Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5003
ENV FLASK_ENV=development


# Expor a porta padrão do Flask
EXPOSE 5003

# Rodar o aplicativo Flask
CMD ["flask", "run", "--host=0.0.0.0"]
