# Usa a imagem oficial do Python
FROM python:3.12

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto para o contêiner
COPY . .

# Instala as dependências
RUN pip install -r requirements.txt

# Expõe a porta 8000 para o servidor FastAPI
EXPOSE 8000

# Comando para rodar o bot
CMD ["python", "main.py"]
