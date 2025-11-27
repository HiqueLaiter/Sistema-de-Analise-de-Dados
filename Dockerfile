# Imagem leve do pyhton para a base
FROM python:3.11-slim

# Define o diretório de trabalho e as vars de ambiente 
WORKDIR /app
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED 1

# Dependencias
COPY requirements.txt .

# Instalação dos Drivers MS SQL
# Instala utilitários do sistema e o Driver ODBC 17 para SQL Server
# É necessário para que o Python se conecte ao Azure SQL
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gnupg2 curl tdsodbc unixodbc unixodbc-dev && \
    # Adiciona a chave GPG da Microsoft
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg && \
    # Adiciona o repositório da Microsoft
    echo "deb [arch=amd64] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list && \
    # Instala o driver
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    # Limpeza para reduzir tamanho da imagem
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte
COPY src/ src/

# Comando de inicialização da aplicação
CMD ["python", "-m", "streamlit", "run", "src/app.py"]