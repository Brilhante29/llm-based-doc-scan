# Base image com Python
FROM python:3.9-slim

# Diretório de trabalho no container
WORKDIR /app

# Atualiza pacotes do sistema e instala dependências
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo requirements.txt dentro da pasta docker
COPY requirements.txt .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código para o diretório de trabalho
COPY . .

# Expõe a porta utilizada pelo Streamlit
EXPOSE 8501

# Comando para rodar a aplicação Streamlit
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
