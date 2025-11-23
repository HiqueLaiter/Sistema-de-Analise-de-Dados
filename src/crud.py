from sqlalchemy.orm import Session
from src import models
from src.models import Transaction, Category, TransactionCreate
from typing import List, Optional
from datetime import datetime
import pandas as pd
import io

# --- Funções CRUD de Transações ---
def create_transaction(db: Session, transaction: TransactionCreate) -> Transaction:
    """
    Cria uma nova transação no banco de dados.

    Args:
        db: Sessão ativa do banco de dados (SQLAlchemy).
        transaction: Objeto Pydantic com os dados da transação.
    """
    # Converte o objeto Pydantic em um dicionário para o modelo SQLAlchemy
    # Usando .model_dump() para compatibilidade com Pydantic v2
    db_transaction = Transaction(**transaction.model_dump()) 
    
    db.add(db_transaction)
    db.commit()      # Salva no banco
    db.refresh(db_transaction) # Atualiza o objeto com o ID gerado
    
    return db_transaction

def get_transactions(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    category_id: Optional[int] = None
) -> List[Transaction]:
    """
    Retorna uma lista paginada de transações, com filtro opcional por categoria.
    """
    query = db.query(Transaction)
    
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
        
    return query.offset(skip).limit(limit).all()


# --- Funções CRUD de Categorias ---
def create_category(db: Session, name: str) -> Category:
    """Cria uma nova categoria (útil para o setup inicial)."""
    db_category = Category(name=name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_categories(db: Session) -> List[Category]:
    """Retorna todas as categorias disponíveis."""
    return db.query(Category).all()


def get_category_by_name(db: Session, name: str):
    """Busca uma categoria pelo nome (para evitar duplicações na importação)."""
    return db.query(Category).filter(Category.name == name).first()


# --- Função Essencial para Análise ---
def get_transactions_dataframe(db: Session) -> pd.DataFrame:
    """
    Busca todas as transações (e categorias) e retorna como um DataFrame do Pandas.
    Esta é a função chave para a análise no 'analyzer.py'.
    """
    # Busca todas as transações e dados de categoria em uma única consulta (JOIN)
    # Importante: A coluna 'amount' deve ser numérica (float) no modelo.
    query = db.query(
        Transaction.date, 
        Transaction.amount, 
        Transaction.description, 
        Category.name.label('category_name') # Renomeia para 'category_name'
    ).join(Category)
    
    # Executa a query e carrega os dados diretamente no DataFrame
    df = pd.read_sql(query.statement, db.bind)
    
    # Garante que a coluna de data seja datetime
    df['date'] = pd.to_datetime(df['date'])
    
    return df