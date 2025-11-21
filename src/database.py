import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

"""
Carrega as variáveis de ambiente do arquivo .env
Isso garante que o código funcione localmente.
Na nuvem, as variáveis serão injetadas diretamente no ambiente do Container App.
"""

load_dotenv() 

# --- Configuração da Conexão ---
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Formato de URL de conexão para o SQLAlchemy: postgresql://user:password@host:port/database
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Cria o Motor de Conexão
# O 'pool_pre_ping=True' ajuda a gerenciar conexões em nuvem de longa duração.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True
)

# Cria a Sessão Local
# SessionLocal será usado nas funções CRUD para interagir com o DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Função de Conveniência (para obter a sessão no Streamlit)
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()