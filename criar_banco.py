import asyncio

from database import Base, engine
from db_models import ContaDB, TransacaoDB


async def criar_banco():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()
    print("Banco de dados e tabelas criados com sucesso!")


if __name__ == "__main__":
    asyncio.run(criar_banco())