import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

"""
Carrega as variáveis de ambiente do arquivo .env
Na nuvem (Azure Container Apps), a variável DATABASE_URL (que passamos no CLI)
será usada como fallback.
"""

load_dotenv() 

# --- Configuração da Conexão ---

# 1. Tenta usar a variável DATABASE_URL injetada pela Azure (Melhor Prática)
# 2. Se não existir (rodando localmente), usa as variáveis individuais
DB_CONNECTION_STRING = os.getenv("DATABASE_URL")

if not DB_CONNECTION_STRING:
    # --- Configurações Locais/Fallback para Azure SQL ---
    DB_HOST = os.getenv("DB_HOST") # Nome do servidor SQL: [server].database.windows.net
    DB_PORT = os.getenv("DB_PORT", "1433") # Porta padrão do SQL Server
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    # Formato de URL de conexão para Azure SQL + PyODBC (dialeto mssql+pyodbc)
    # CRUCIAL: O parâmetro '?driver=ODBC+Driver+17+for+SQL+Server' é necessário para a conexão Azure.
    DB_CONNECTION_STRING = (
        f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server"
    )


# Cria o Motor de Conexão
# O 'pool_pre_ping=True' ajuda a gerenciar conexões em nuvem de longa duração.
# O connect_args é adicionado para aumentar a estabilidade.
engine = create_engine(
    DB_CONNECTION_STRING, 
    pool_pre_ping=True,
    # Adiciona argumentos de conexão específicos para o Azure SQL
    connect_args={
        "timeout": 30,  # Tempo limite de conexão
    }
)

# Cria a Sessão Local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Função de Conveniência (para obter a sessão no Streamlit)
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        # Garante que a sessão é fechada após o uso, liberando recursos
        db.close()