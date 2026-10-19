
from typing import Literal
from pydantic import BaseModel, Field


class ContaBancaria(BaseModel):
    titular: str = Field(min_length=2, description="Nome do titular da conta")
    saldo: float = Field(default=0.0, ge=0, description="Saldo da conta")


class Transacao(BaseModel):
    tipo: Literal["deposito", "saque"] = Field(
        description="Tipo de transação: deposito ou saque"
    )
    valor: float = Field(
        gt=0,
        description="Valor da transação, maior que zero"
    )
