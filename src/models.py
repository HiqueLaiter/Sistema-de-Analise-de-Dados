from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

Base = declarative_base()

# =======================================================
# 1. Modelos de Banco de Dados (SQLAlchemy)
# =======================================================

class Category(Base):
    """Tabela de Categorias Financeiras."""
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    # CORREÇÃO: String(255) define um limite aceito pelo SQL Server para índices
    name = Column(String(255), unique=True, index=True, nullable=False)
    
    transactions = relationship("Transaction", back_populates="category")

class Transaction(Base):
    """Tabela de Transações Financeiras."""
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    amount = Column(Float, nullable=False)
    # CORREÇÃO: String(255) aqui também
    description = Column(String(255), index=True)
    
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    
    category = relationship("Category", back_populates="transactions")

# =======================================================
# 2. Schemas da API (Pydantic)
# =======================================================

class TransactionBase(BaseModel):
    date: datetime
    amount: float
    description: Optional[str] = None
    category_id: int

class TransactionCreate(TransactionBase):
    pass

class TransactionRead(TransactionBase):
    id: int
    class Config:
        from_attributes = True