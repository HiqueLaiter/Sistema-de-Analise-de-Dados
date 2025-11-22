# --- 1. Base Image: Imagem base oficial do Python ---
# Versão slim para ter um container menor, mas que ainda contenha o essencial para rodar o Python.
FROM python:3.11-slim

# --- 2. Setup do Ambiente ---
# Define a pasta de trabalho dentro do container.
WORKDIR /app

# Define variáveis de ambiente (Útil para a conexão com o banco de dados)
# As credenciais reais serão passadas via Docker Compose ou Azure.
ENV PYTHONUNBUFFERED 1
ENV STREAMLIT_SERVER_PORT 8501
EXPOSE 8501

# --- 3. Instalação de Dependências ---
# Copia o arquivo requirements.txt primeiro para aproveitar o cache do Docker.
# Se apenas o requirements.txt mudar, o Docker não precisa rodar a linha 3 novamente.
COPY requirements.txt .

# Instala as dependências. O --no-cache-dir economiza espaço no container.
RUN pip install --no-cache-dir -r requirements.txt

# --- 4. Copiar o Código Fonte ---
# Copia o restante do código do projeto para a pasta /app dentro do container.
# Copiamos src/ e todos os arquivos relevantes.
COPY src/ src/

# --- 5. Comando de Execução ---
# Define o comando que será executado quando o container iniciar.
# O Streamlit usa 'streamlit run' para iniciar a aplicação.
CMD ["streamlit", "run", "src/app.py"]