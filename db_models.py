
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class ContaDB(Base):
    __tablename__ = "contas"

    id = Column(Integer, primary_key=True, index=True)
    titular = Column(String, nullable=False)
    saldo = Column(Float, nullable=False, default=0.0)

    transacoes = relationship(
        "TransacaoDB",
        back_populates="conta",
        cascade="all, delete-orphan",
    )


class TransacaoDB(Base):
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True, index=True)
    conta_id = Column(Integer, ForeignKey("contas.id"), nullable=False)
    tipo = Column(String, nullable=False)
    valor = Column(Float, nullable=False)
    saldo_apos_transacao = Column(Float, nullable=False)

    conta = relationship(
        "ContaDB",
        back_populates="transacoes",
    )
