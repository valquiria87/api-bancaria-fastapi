
import os
from contextlib import asynccontextmanager
from secrets import compare_digest

from fastapi import Depends, FastAPI, HTTPException, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import Base, engine, get_db
from db_models import ContaDB, TransacaoDB
from models import ContaBancaria, Transacao
from auth import criar_token, verificar_token

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="API Bancária",
    description=(
        "API assíncrona para gerenciamento de contas "
        "correntes e transações bancárias."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.post(
    "/token",
    tags=["Autenticação"],
    summary="Autenticar usuário",
    description=(
        "Valida usuário e senha configurados nas variáveis de ambiente "
        "e retorna um token JWT para acessar rotas protegidas."
    ),
    responses={
        401: {"description": "Usuário ou senha incorretos"},
        500: {"description": "Credenciais não configuradas"},
    },
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    usuario_correto = os.getenv("API_USERNAME")
    senha_correta = os.getenv("API_PASSWORD")

    if not usuario_correto or not senha_correta:
        raise HTTPException(
            status_code=500,
            detail="Credenciais de login não configuradas no ambiente",
        )

    if not (
        compare_digest(form_data.username, usuario_correto)
        and compare_digest(form_data.password, senha_correta)
    ):
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = criar_token({"sub": form_data.username})

    return {
        "access_token": token,
        "token_type": "bearer",
    }

@app.get(
    "/",
    tags=["Geral"],
    summary="Verificar funcionamento da API",
    description="Retorna uma mensagem indicando que a API está funcionando.",
)
async def inicio():
    return {"mensagem": "API Bancária funcionando!"}


@app.post(
    "/accounts",
    status_code=201,
    summary="Criar conta bancária",
    description="Cria uma conta bancária com titular e saldo inicial não negativo.",
)
async def criar_conta(
    conta: ContaBancaria,
    db: AsyncSession = Depends(get_db),
):
    nova_conta = ContaDB(
        titular=conta.titular,
        saldo=conta.saldo,
    )

    db.add(nova_conta)
    await db.commit()
    await db.refresh(nova_conta)

    return {
        "id": nova_conta.id,
        "titular": nova_conta.titular,
        "saldo": nova_conta.saldo,
        "transacoes": [],
    }


@app.get(
    "/accounts",
    summary="Listar contas bancárias",
    description="Retorna as contas cadastradas e o histórico de suas transações.",
)
async def listar_contas(db: AsyncSession = Depends(get_db)):
    consulta = (
        select(ContaDB)
        .options(selectinload(ContaDB.transacoes))
    )

    resultado = await db.execute(consulta)
    contas_db = resultado.scalars().all()

    return [
        {
            "id": conta.id,
            "titular": conta.titular,
            "saldo": conta.saldo,
            "transacoes": [
                {
                    "tipo": transacao.tipo,
                    "valor": transacao.valor,
                    "saldo_apos_transacao": (
                        transacao.saldo_apos_transacao
                    ),
                }
                for transacao in conta.transacoes
            ],
        }
        for conta in contas_db
    ]


@app.post(
    "/accounts/{account_id}/transactions",
    summary="Realizar transação bancária",
    description=(
        "Realiza um depósito ou saque. Exige autenticação JWT "
        "e valida se há saldo suficiente para saques."
    ),
    responses={
        400: {"description": "Saldo insuficiente"},
        401: {"description": "Token inválido ou não informado"},
        404: {"description": "Conta não encontrada"},
    },
)
async def criar_transacao(
    transacao: Transacao,
    account_id: int = Path(
        description="Identificador numérico da conta bancária",
        gt=0,
    ),
    db: AsyncSession = Depends(get_db),
    usuario_atual: dict = Depends(verificar_token),
):
    resultado = await db.execute(
        select(ContaDB).where(ContaDB.id == account_id)
    )
    conta = resultado.scalar_one_or_none()

    if conta is None:
        raise HTTPException(
            status_code=404,
            detail="Conta não encontrada",
        )

    if transacao.tipo == "saque" and transacao.valor > conta.saldo:
        raise HTTPException(
            status_code=400,
            detail="Saldo insuficiente",
        )

    if transacao.tipo == "deposito":
        conta.saldo += transacao.valor
    else:
        conta.saldo -= transacao.valor

    nova_transacao = TransacaoDB(
        conta_id=conta.id,
        tipo=transacao.tipo,
        valor=transacao.valor,
        saldo_apos_transacao=conta.saldo,
    )

    db.add(nova_transacao)
    await db.commit()
    await db.refresh(conta)

    return {
        "mensagem": "Transação realizada com sucesso",
        "conta_id": conta.id,
        "tipo": transacao.tipo,
        "valor": transacao.valor,
        "saldo_atual": conta.saldo,
    }


@app.get(
    "/accounts/{account_id}/statement",
    summary="Consultar extrato bancário",
    description=(
        "Retorna o saldo atual e o histórico de transações "
        "da conta. Exige autenticação JWT."
    ),
)
async def consultar_extrato(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_atual: dict = Depends(verificar_token),
):
    consulta = (
        select(ContaDB)
        .options(selectinload(ContaDB.transacoes))
        .where(ContaDB.id == account_id)
    )

    resultado = await db.execute(consulta)
    conta = resultado.scalar_one_or_none()

    if conta is None:
        raise HTTPException(
            status_code=404,
            detail="Conta não encontrada",
        )

    return {
        "conta_id": conta.id,
        "titular": conta.titular,
        "saldo_atual": conta.saldo,
        "transacoes": [
            {
                "tipo": transacao.tipo,
                "valor": transacao.valor,
                "saldo_apos_transacao": (
                    transacao.saldo_apos_transacao
                ),
            }
            for transacao in conta.transacoes
        ],
    }
