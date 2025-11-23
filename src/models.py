# src/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Base para o SQLAlchemy (Cria o objeto base para o mapeamento objeto-relacional)
Base = declarative_base()

# =======================================================
# 1. Modelos de Banco de Dados (SQLAlchemy)
# Mapeia classes Python para as tabelas do PostgreSQL
# =======================================================

class Category(Base):
    """Tabela de Categorias Financeiras."""
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    
    # Relacionamento de volta para as transações
    transactions = relationship("Transaction", back_populates="category")

class Transaction(Base):
    """Tabela de Transações Financeiras."""
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    # Coluna 'amount' armazena o valor. Positivo para entrada (receita), negativo para saída (despesa)
    amount = Column(Float, nullable=False)
    description = Column(String, index=True)
    
    # Chave Estrangeira: liga esta transação a uma categoria
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    
    # Define o relacionamento: permite acessar Category.name diretamente do objeto Transaction
    category = relationship("Category", back_populates="transactions")

# =======================================================
# 2. Schemas da API (Pydantic)
# Usados para validação de dados de entrada/saída da aplicação
# =======================================================

class TransactionBase(BaseModel):
    """Schema base para os atributos da transação."""
    date: datetime
    amount: float
    description: Optional[str] = None
    category_id: int

class TransactionCreate(TransactionBase):
    """Schema usado para CRIAR uma nova transação (o que o usuário envia)."""
    # Não inclui o 'id' pois ele é gerado pelo banco.
    pass

class TransactionRead(TransactionBase):
    """Schema usado para RETORNAR dados de uma transação (o que a API retorna)."""
    id: int
    
    class Config:
        # Permite que o Pydantic leia diretamente dos objetos SQLAlchemy
        from_attributes = True